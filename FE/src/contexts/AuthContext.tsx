import React, { createContext, useContext, useState, useEffect, type ReactNode } from "react";

// User profile interface matching backend response
export interface UserProfile {
  user_id: number;
  username: string | null;
  email: string;
  role: "student" | "lecturer" | "manager";
  full_name: string;
  // Student-specific
  student_id?: number;
  major?: string;
  current_gpa?: number;
  // Lecturer-specific
  title?: string;
  department?: string;
  // Manager-specific
  office?: string;
  position?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: UserProfile;
}

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_BASE_URL = "http://localhost:8000";

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load user from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    const storedUser = localStorage.getItem("user");

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
    setIsLoading(false);
  }, []);

  const login = async (username: string, password: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Login failed");
      }

      const data: LoginResponse = await response.json();

      // Store in state and localStorage
      setToken(data.access_token);
      setUser(data.user);
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Login failed";
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  };

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!token && !!user,
    isLoading,
    login,
    logout,
    error,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

// Helper to get dashboard route based on user role
export const getDashboardRoute = (role: string): string => {
  switch (role) {
    case "student":
      return "/student-dashboard";
    case "lecturer":
      return "/lecturer-dashboard";
    case "manager":
      return "/manager-dashboard";
    default:
      return "/login";
  }
};

// Navigation links for each role
export const getNavLinks = (role: string) => {
  switch (role) {
    case "student":
      return [
        { path: "/student-dashboard", label: "Dashboard" },
        { path: "/my-courses", label: "My Courses" },
        { path: "/student-feedback", label: "Feedback" },
      ];
    case "lecturer":
      return [
        { path: "/lecturer-dashboard", label: "Dashboard" },
        { path: "/my-courses", label: "My Courses" },
        { path: "/lecturer-feedback", label: "Feedback" },
      ];
    case "manager":
      return [
        { path: "/manager-dashboard", label: "Dashboard" },
      ];
    default:
      return [];
  }
};
