# Frontend Integration Guide

This guide explains how to integrate the Brahmavastu backend authentication system with your frontend application.

## 🔐 Authentication Endpoints

### Base URL
```
http://localhost:8000/api/auth
```

## 📋 API Endpoints

### 1. User Registration
```http
POST /api/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "phone": "+1234567890"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "role": "user",
  "avatar_url": null,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 2. User Login
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Get Current User
```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "avatar_url": null,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 4. Check Authentication Status
```http
GET /api/auth/check-auth
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "authenticated": true,
  "user_id": "1",
  "role": "user"
}
```

### 5. Logout
```http
POST /api/auth/logout
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

### 6. Refresh Token
```http
POST /api/auth/refresh
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 7. OAuth Login (Google)
```http
POST /api/auth/oauth
Content-Type: application/json

{
  "provider": "google",
  "token": "google_id_token_here"
}
```

### 8. Forgot Password
```http
POST /api/auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```

### 9. Reset Password
```http
POST /api/auth/reset-password
Content-Type: application/json

{
  "token": "reset_token_here",
  "new_password": "newpassword123"
}
```

## 🚀 Frontend Implementation Examples

### React/Next.js Example

```javascript
// auth.js - Authentication utilities
class AuthService {
  constructor() {
    this.baseURL = 'http://localhost:8000/api/auth';
    this.tokenKey = 'brahmavastu_token';
  }

  // Store token in localStorage
  setToken(token) {
    localStorage.setItem(this.tokenKey, token);
  }

  // Get token from localStorage
  getToken() {
    return localStorage.getItem(this.tokenKey);
  }

  // Remove token from localStorage
  removeToken() {
    localStorage.removeItem(this.tokenKey);
  }

  // Get auth headers
  getAuthHeaders() {
    const token = this.getToken();
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    };
  }

  // Login
  async login(email, password) {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${this.baseURL}/login`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  // Register
  async register(userData) {
    const response = await fetch(`${this.baseURL}/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(userData)
    });

    if (!response.ok) {
      throw new Error('Registration failed');
    }

    return await response.json();
  }

  // Get current user
  async getCurrentUser() {
    const response = await fetch(`${this.baseURL}/me`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to get user');
    }

    return await response.json();
  }

  // Check if user is authenticated
  async checkAuth() {
    try {
      const response = await fetch(`${this.baseURL}/check-auth`, {
        headers: this.getAuthHeaders()
      });

      if (!response.ok) {
        return false;
      }

      const data = await response.json();
      return data.authenticated;
    } catch (error) {
      return false;
    }
  }

  // Logout
  async logout() {
    try {
      await fetch(`${this.baseURL}/logout`, {
        method: 'POST',
        headers: this.getAuthHeaders()
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.removeToken();
    }
  }

  // Refresh token
  async refreshToken() {
    const response = await fetch(`${this.baseURL}/refresh`, {
      method: 'POST',
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error('Token refresh failed');
    }

    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  }
}

export const authService = new AuthService();
```

### React Hook Example

```javascript
// useAuth.js - React hook for authentication
import { useState, useEffect, createContext, useContext } from 'react';
import { authService } from './auth';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const isAuth = await authService.checkAuth();
      if (isAuth) {
        const userData = await authService.getCurrentUser();
        setUser(userData);
        setAuthenticated(true);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const data = await authService.login(email, password);
      const userData = await authService.getCurrentUser();
      setUser(userData);
      setAuthenticated(true);
      return data;
    } catch (error) {
      throw error;
    }
  };

  const register = async (userData) => {
    try {
      const data = await authService.register(userData);
      return data;
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
      setUser(null);
      setAuthenticated(false);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const value = {
    user,
    authenticated,
    loading,
    login,
    register,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
```

### Login Component Example

```jsx
// LoginForm.jsx
import React, { useState } from 'react';
import { useAuth } from './useAuth';

const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      // Redirect to dashboard or home page
      window.location.href = '/dashboard';
    } catch (error) {
      setError('Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="login-form">
      <h2>Login to Brahmavastu</h2>
      
      {error && <div className="error">{error}</div>}
      
      <div className="form-group">
        <label htmlFor="email">Email</label>
        <input
          type="email"
          id="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="password">Password</label>
        <input
          type="password"
          id="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>

      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
};

export default LoginForm;
```

### Protected Route Example

```jsx
// ProtectedRoute.jsx
import React from 'react';
import { useAuth } from './useAuth';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children, requiredRole = null }) => {
  const { user, authenticated, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!authenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && user?.role !== requiredRole) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};

export default ProtectedRoute;
```

## 🔒 Role-Based Access Control

### Check User Role
```javascript
// Check if user has admin role
const { user } = useAuth();
const isAdmin = user?.role === 'admin';

// Check if user has specific permissions
const hasPermission = (permission) => {
  switch (permission) {
    case 'admin':
      return user?.role === 'admin';
    case 'consultant':
      return ['admin', 'consultant'].includes(user?.role);
    default:
      return true;
  }
};
```

### Conditional Rendering
```jsx
const Dashboard = () => {
  const { user } = useAuth();

  return (
    <div>
      <h1>Dashboard</h1>
      
      {/* Show for all users */}
      <div>Welcome, {user?.full_name}!</div>
      
      {/* Show only for admin */}
      {user?.role === 'admin' && (
        <div>
          <h2>Admin Panel</h2>
          <button>Manage Users</button>
          <button>View Analytics</button>
        </div>
      )}
      
      {/* Show for admin and consultant */}
      {['admin', 'consultant'].includes(user?.role) && (
        <div>
          <h2>Consultant Tools</h2>
          <button>View Consultations</button>
        </div>
      )}
    </div>
  );
};
```

## 🌐 CORS Configuration

Make sure your backend allows requests from your frontend domain:

```python
# In your FastAPI app
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📱 Mobile App Integration

For React Native or mobile apps, use the same API endpoints with appropriate HTTP client:

```javascript
// React Native example
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/auth';

const authAPI = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
authAPI.interceptors.request.use((config) => {
  const token = AsyncStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const login = async (email, password) => {
  const formData = new FormData();
  formData.append('username', email);
  formData.append('password', password);

  const response = await authAPI.post('/login', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  await AsyncStorage.setItem('token', response.data.access_token);
  return response.data;
};
```

## 🚨 Error Handling

```javascript
// Global error handler
const handleAPIError = (error) => {
  if (error.response) {
    switch (error.response.status) {
      case 401:
        // Unauthorized - redirect to login
        authService.removeToken();
        window.location.href = '/login';
        break;
      case 403:
        // Forbidden - show access denied
        alert('Access denied');
        break;
      case 400:
        // Bad request - show validation errors
        return error.response.data.detail;
      default:
        alert('An error occurred');
    }
  } else {
    alert('Network error');
  }
};
```

## 🔧 Testing

Test your authentication flow:

1. **Register a new user**
2. **Login with credentials**
3. **Access protected routes**
4. **Check role-based access**
5. **Test logout**
6. **Test token refresh**

## 📝 Environment Variables

Set up your frontend environment variables:

```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_AUTH_URL=http://localhost:8000/api/auth
```

This integration guide provides everything you need to connect your frontend to the Brahmavastu authentication system! 🎉 