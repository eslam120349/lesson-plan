// Main React application entry point
const { useState, useEffect } = React;
const { BrowserRouter, Routes, Route, Navigate, useNavigate, Link } = ReactRouterDOM;

// Configure Axios
axios.defaults.headers.common['Content-Type'] = 'application/json';
axios.defaults.headers.common['Accept'] = 'application/json';

const App = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if user is authenticated on component mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await axios.get('/api/user');
        setUser(response.data);
      } catch (err) {
        console.log('Not logged in');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  // Handle user login
  const handleLogin = async (credentials) => {
    try {
      setError(null);
      const response = await axios.post('/api/login', credentials);
      setUser(response.data.user);
      return true;
    } catch (err) {
      setError(err.response?.data?.message || 'Login failed');
      return false;
    }
  };

  // Handle user registration
  const handleRegister = async (userData) => {
    try {
      setError(null);
      await axios.post('/api/register', userData);
      return true;
    } catch (err) {
      setError(err.response?.data?.message || 'Registration failed');
      return false;
    }
  };

  // Handle user logout
  const handleLogout = async () => {
    try {
      await axios.post('/api/logout');
      setUser(null);
    } catch (err) {
      console.error('Logout error:', err);
    }
  };

  // Protected route component
  const PrivateRoute = ({ component: Component, ...rest }) => (
    <Route
      {...rest}
      render={(props) =>
        loading ? (
          <div className="text-center py-5">
            <div className="spinner-border" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        ) : user ? (
          <Component {...props} user={user} />
        ) : (
          <Redirect to="/login" />
        )
      }
    />
  );

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  // A modified PrivateRoute component for React Router v6
  const PrivateRoute = ({ children }) => {
    return user ? children : <Navigate to="/login" replace />;
  };

  return (
    <BrowserRouter>
      <div className="d-flex flex-column min-vh-100">
        <Navigation user={user} onLogout={handleLogout} />
        
        <main className="flex-grow-1">
          <div className="container mt-4">
            {error && (
              <div className="alert alert-danger alert-dismissible fade show" role="alert">
                {error}
                <button type="button" className="btn-close" onClick={() => setError(null)}></button>
              </div>
            )}
            
            <Routes>
              <Route path="/login" element={user ? <Navigate to="/dashboard" replace /> : <Auth onLogin={handleLogin} onRegister={handleRegister} />} />
              
              <Route path="/dashboard" element={
                <PrivateRoute>
                  <Dashboard user={user} />
                </PrivateRoute>
              } />
              
              <Route path="/lessons/new" element={
                <PrivateRoute>
                  <LessonForm user={user} />
                </PrivateRoute>
              } />
              
              <Route path="/lessons/:id/edit" element={
                <PrivateRoute>
                  <LessonForm user={user} />
                </PrivateRoute>
              } />
              
              <Route path="/lessons/:id" element={
                <PrivateRoute>
                  <LessonView user={user} />
                </PrivateRoute>
              } />
              
              <Route path="/lessons" element={
                <PrivateRoute>
                  <LessonList user={user} />
                </PrivateRoute>
              } />
              
              <Route path="/" element={user ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />} />
            </Routes>
          </div>
        </main>
        
        <footer className="bg-dark py-3 mt-auto">
          <div className="container text-center">
            <p className="mb-0 text-light">© {new Date().getFullYear()} Teacher's Lesson Planner</p>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
};

// Render the app
const root = ReactDOM.createRoot(document.getElementById('app'));
root.render(<App />);
