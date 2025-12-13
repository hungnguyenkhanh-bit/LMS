"""
Prediction Service Module

This module handles loading the trained ML model and making predictions
for student GPA and pass/fail outcomes.
"""

import os
import pickle
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MODEL_PATH = Path(__file__).parent / "models" / "student_prediction_model.pkl"
MODEL_VERSION = "v1.0"
PASS_THRESHOLD = 2.0  # GPA threshold for pass/fail determination


class PredictionService:
    """
    Singleton service for loading and using the student prediction model.
    """

    _instance = None
    _model = None
    _scaler = None
    _feature_names = None
    _model_loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PredictionService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the prediction service and load the model."""
        if not self._model_loaded:
            self._load_model()

    def _load_model(self):
        """Load the trained model from disk."""
        try:
            if not MODEL_PATH.exists():
                raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

            with open(MODEL_PATH, "rb") as f:
                model_data = pickle.load(f)

            # Handle different possible pickle formats
            if isinstance(model_data, dict):
                # If the pickle contains a dictionary with model and metadata
                self._model = model_data.get("model")
                self._scaler = model_data.get("scaler")
                self._feature_names = model_data.get(
                    "feature_names", self._get_default_features()
                )
            else:
                print("DEBUGGING: Model data is not a dictionary")
                # If the pickle contains just the model
                self._model = model_data
                self._scaler = None
                self._feature_names = self._get_default_features()

            self._model_loaded = True
            logger.info(f"Model loaded successfully from {MODEL_PATH}")
            logger.info(f"Expected features: {self._feature_names}")
            if self._scaler:
                logger.info("StandardScaler loaded successfully")
            else:
                logger.warning(
                    "No scaler found - predictions may be inaccurate without proper scaling"
                )

        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def _get_default_features(self) -> List[str]:
        """
        Return default feature names based on common academic prediction features.
        These should match the EXACT names used during model training.
        NOTE: The CSV uses 'assignment_grade', not 'assignment_score'
        """
        return [
            "attendance_rate",
            "avg_quiz_score",
            "assignment_grade",  # Must match CSV column name
            "study_hours_per_week",
        ]

    def get_feature_names(self) -> List[str]:
        """Return the list of expected feature names."""
        return self._feature_names.copy()

    def predict_gpa(self, features: List[float]) -> Tuple[float, float]:
        """
        Predict GPA based on input features.

        Args:
            features: List of feature values in the correct order

        Returns:
            Tuple of (predicted_gpa, confidence_score)

        Raises:
            ValueError: If features length doesn't match expected
            RuntimeError: If model is not loaded
        """
        if not self._model_loaded or self._model is None:
            raise RuntimeError("Model is not loaded")

        if len(features) != len(self._feature_names):
            raise ValueError(
                f"Expected {len(self._feature_names)} features, got {len(features)}. "
                f"Expected features: {self._feature_names}"
            )

        try:
            # Convert to DataFrame with feature names to match training format
            # The model was trained on a DataFrame, so we need to predict with the same format
            features_df = pd.DataFrame([features], columns=self._feature_names)

            # Apply scaling if scaler is available
            if self._scaler is not None:
                features_scaled = self._scaler.transform(features_df)
                predicted_gpa = float(self._model.predict(features_scaled)[0])
            else:
                # No scaling - predict directly with DataFrame
                predicted_gpa = float(self._model.predict(features_df)[0])
            print("DEBUGGING: Predicted GPA", predicted_gpa)

            # Clamp GPA to valid range [0.0, 4.0]
            predicted_gpa = max(0.0, min(4.0, predicted_gpa))

            # Calculate confidence score (pass original features as array for heuristic)
            confidence = self._calculate_confidence(
                np.array(features).reshape(1, -1), predicted_gpa
            )

            return predicted_gpa, confidence

        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise

    def _calculate_confidence(
        self, features: "np.ndarray", predicted_gpa: float
    ) -> float:
        """
        Calculate confidence score for the prediction.

        For regression models without predict_proba, we use alternative methods:
        - Check if model has prediction intervals or uncertainty estimates
        - Use distance from training data
        - Use simple heuristics based on feature quality
        """
        try:
            # Try to get prediction probability if available (for classifiers)
            if hasattr(self._model, "predict_proba"):
                proba = self._model.predict_proba(features)
                confidence = float(np.max(proba))
            # Try to get standard deviation if available (for some regressors)
            elif hasattr(self._model, "predict") and hasattr(self._model, "get_params"):
                # For regression, use a heuristic based on the predicted value
                # Higher GPA predictions typically have lower variance
                # This is a simplified approach
                confidence = self._heuristic_confidence(features, predicted_gpa)
            else:
                confidence = self._heuristic_confidence(features, predicted_gpa)

            # Ensure confidence is in [0, 1] range
            return max(0.0, min(1.0, confidence))

        except Exception as e:
            logger.warning(f"Could not calculate confidence: {str(e)}")
            return 0.7  # Default moderate confidence

    def _heuristic_confidence(
        self, features: "np.ndarray", predicted_gpa: float
    ) -> float:
        """
        Calculate confidence using heuristics based on feature quality.

        Args:
            features: Input feature array
            predicted_gpa: Predicted GPA value

        Returns:
            Confidence score between 0 and 1
        """

        # Base confidence
        confidence = 0.75

        # Extract key features (assuming default feature order)
        if features.shape[1] >= 4:
            attendance_rate = features[0, 0]
            avg_quiz_score = features[0, 1]
            assignment_grade = features[0, 2]
            study_hours_per_week = features[0, 3]

            # Adjust confidence based on data quality indicators

            # Higher attendance correlates with more reliable predictions
            if attendance_rate > 0.8:
                confidence += 0.1
            elif attendance_rate < 0.5:
                confidence -= 0.1

            # Consistency between quiz and assignment scores
            score_consistency = 1.0 - abs(avg_quiz_score - assignment_grade)
            confidence += score_consistency * 0.1

        return min(1.0, max(0.5, confidence))

    def determine_pass_fail(
        self, predicted_gpa: float, threshold: float = PASS_THRESHOLD
    ) -> str:
        """
        Determine pass or fail based on predicted GPA.

        Args:
            predicted_gpa: The predicted GPA value
            threshold: GPA threshold for passing (default: 2.0)

        Returns:
            "pass" or "fail"
        """
        return "pass" if predicted_gpa >= threshold else "fail"

    def generate_recommendations(
        self, features_dict: Dict[str, float], predicted_gpa: float, pass_fail: str
    ) -> str:
        """
        Generate personalized recommendations based on student data.

        Args:
            features_dict: Dictionary mapping feature names to values
            predicted_gpa: Predicted GPA
            pass_fail: "pass" or "fail" status

        Returns:
            Recommendations string
        """
        recommendations = []

        # Extract features
        attendance_rate = features_dict.get("attendance_rate", 0)
        avg_quiz_score = features_dict.get("avg_quiz_score", 0)
        assignment_grade = features_dict.get("assignment_grade", 0)
        study_hours = features_dict.get("study_hours_per_week", 0)

        # Generate targeted recommendations
        if pass_fail == "fail":
            recommendations.append(
                "⚠️ You are at risk of not meeting the minimum GPA requirement."
            )

        if attendance_rate < 0.7:
            recommendations.append(
                f"📚 Improve attendance: Your current rate is {attendance_rate * 100:.0f}%. "
                "Aim for at least 80% attendance to improve understanding and performance."
            )

        if avg_quiz_score < 60:
            recommendations.append(
                f"📝 Focus on quiz preparation: Your average quiz score is {avg_quiz_score:.1f}%. "
                "Review lecture materials regularly and practice with sample questions."
            )

        if assignment_grade < 70:
            recommendations.append(
                f"✍️ Improve assignment quality: Your average assignment grade is {assignment_grade:.1f}%. "
                "Start assignments early and seek help from lecturers or peers when needed."
            )

        if study_hours < 10:
            recommendations.append(
                f"📖 Increase study time: You're studying {study_hours:.0f} hours/week. "
                "Aim for 10-15 hours per week for better comprehension and retention."
            )

        # Positive reinforcement for good performance
        if pass_fail == "pass" and predicted_gpa >= 3.0:
            recommendations.append(
                f"🌟 Excellent work! Keep maintaining your good habits: "
                f"high attendance, consistent studying, and timely submissions."
            )
        elif pass_fail == "pass":
            recommendations.append(
                "✅ You're on track to pass. Focus on areas mentioned above to improve your GPA further."
            )

        # If no specific issues found
        if not recommendations:
            recommendations.append(
                "Continue your current study habits and maintain consistent performance across all areas."
            )

        return " ".join(recommendations)


# Singleton instance
_prediction_service = None


def get_prediction_service() -> PredictionService:
    """
    Get or create the singleton prediction service instance.

    Returns:
        PredictionService instance
    """
    global _prediction_service
    if _prediction_service is None:
        _prediction_service = PredictionService()
    return _prediction_service


def predict_student_outcome(
    attendance_rate: float,
    avg_quiz_score: float,
    assignment_score: float,
    study_hours_per_week: float,
) -> Dict:
    """
    Convenience function for making predictions.

    Args:
        current_gpa: Current GPA (0.0 - 4.0)
        attendance_rate: Attendance rate (0.0 - 1.0)
        avg_quiz_score: Average quiz score (0 - 100)
        avg_assignment_score: Average assignment score (0 - 100)
        late_submissions: Number of late submissions
        courses_enrolled: Number of courses currently enrolled
        study_hours_per_week: Hours spent studying per week

    Returns:
        Dictionary containing prediction results
    """
    service = get_prediction_service()

    # Build features list in correct order
    # NOTE: No normalization applied - model was trained on raw values
    features = [
        attendance_rate,
        avg_quiz_score,  # Raw value (0-100)
        assignment_score,  # Raw value (0-100)
        study_hours_per_week,
    ]

    # Get prediction
    predicted_gpa, confidence = service.predict_gpa(features)
    pass_fail = service.determine_pass_fail(predicted_gpa)

    # Build features dict for recommendations
    features_dict = {
        "attendance_rate": attendance_rate,
        "avg_quiz_score": avg_quiz_score,
        "assignment_grade": assignment_score,  # Map API parameter to model feature name
        "study_hours_per_week": study_hours_per_week,
    }

    recommendations = service.generate_recommendations(
        features_dict, predicted_gpa, pass_fail
    )

    return {
        "predicted_gpa": round(predicted_gpa, 2),
        "confidence": round(confidence, 2),
        "pass_fail": pass_fail,
        "threshold": PASS_THRESHOLD,
        "recommendations": recommendations,
        "model_version": MODEL_VERSION,
    }


if __name__ == "__main__":
    # Test the prediction service
    try:
        service = get_prediction_service()
        print(f"Model loaded successfully!")
        print(f"Expected features: {service.get_feature_names()}")
        print(f"\nModel version: {MODEL_VERSION}")
        print(f"Pass/fail threshold: {PASS_THRESHOLD}")

        # Test prediction
        test_result = predict_student_outcome(
            attendance_rate=0.85,
            avg_quiz_score=75.0,
            assignment_score=80.0,
            study_hours_per_week=12.0,
        )

        print("\n=== Test Prediction ===")
        print(f"Predicted GPA: {test_result['predicted_gpa']}")
        print(f"Confidence: {test_result['confidence'] * 100:.0f}%")
        print(f"Status: {test_result['pass_fail'].upper()}")
        print(f"Recommendations: {test_result['recommendations']}")

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback

        traceback.print_exc()
