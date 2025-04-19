import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const Dashboard = ({ user }) => {
  const [lessons, setLessons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    totalLessons: 0,
    totalPresentations: 0,
    recentActivity: []
  });

  // Fetch user's lessons on component mount
  useEffect(() => {
    const fetchLessons = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/lessons');
        setLessons(response.data);
        
        // Calculate stats
        const totalLessons = response.data.length;
        const totalPresentations = response.data.reduce(
          (count, lesson) => count + lesson.presentations.length, 0
        );
        
        // Get 5 most recent lessons
        const recentActivity = [...response.data]
          .sort((a, b) => new Date(b.date_modified) - new Date(a.date_modified))
          .slice(0, 5);
        
        setStats({
          totalLessons,
          totalPresentations,
          recentActivity
        });
      } catch (err) {
        setError('Failed to load lessons. Please try again later.');
        console.error('Error fetching lessons:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchLessons();
  }, []);

  // Format date for display
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  if (loading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        {error}
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="row mb-4">
        <div className="col-12">
          <div className="card shadow-sm">
            <div className="card-body">
              <h2 className="card-title">Welcome, {user.name}!</h2>
              <p className="card-text">
                Create, manage, and generate lesson plans with our AI-powered platform.
              </p>
              <Link to="/lessons/new" className="btn btn-primary">
                <i className="bi bi-plus-circle me-2"></i>
                Create New Lesson Plan
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="row mb-4">
        <div className="col-md-4 mb-3 mb-md-0">
          <div className="card shadow-sm h-100">
            <div className="card-body text-center">
              <h5 className="card-title">Lesson Plans</h5>
              <p className="display-4">{stats.totalLessons}</p>
              <Link to="/lessons" className="btn btn-sm btn-outline-primary">View All</Link>
            </div>
          </div>
        </div>
        
        <div className="col-md-4 mb-3 mb-md-0">
          <div className="card shadow-sm h-100">
            <div className="card-body text-center">
              <h5 className="card-title">Presentations</h5>
              <p className="display-4">{stats.totalPresentations}</p>
              <Link to="/lessons" className="btn btn-sm btn-outline-primary">View All</Link>
            </div>
          </div>
        </div>
        
        <div className="col-md-4">
          <div className="card shadow-sm h-100">
            <div className="card-body text-center">
              <h5 className="card-title">Quick Actions</h5>
              <div className="d-grid gap-2">
                <Link to="/lessons/new" className="btn btn-sm btn-outline-primary">
                  <i className="bi bi-plus-circle me-2"></i>New Lesson
                </Link>
                <Link to="/lessons" className="btn btn-sm btn-outline-secondary">
                  <i className="bi bi-journal-text me-2"></i>My Lessons
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-12">
          <div className="card shadow-sm">
            <div className="card-header">
              <h5 className="mb-0">Recent Activity</h5>
            </div>
            <div className="card-body">
              {stats.recentActivity.length > 0 ? (
                <div className="list-group list-group-flush">
                  {stats.recentActivity.map(lesson => (
                    <Link 
                      key={lesson.id} 
                      to={`/lessons/${lesson.id}`} 
                      className="list-group-item list-group-item-action"
                    >
                      <div className="d-flex w-100 justify-content-between">
                        <h6 className="mb-1">{lesson.topic}</h6>
                        <small>{formatDate(lesson.date_modified)}</small>
                      </div>
                      <p className="mb-1">
                        Grade: {lesson.grade_level} | 
                        Strategy: {lesson.teaching_strategy.replace('_', ' ')}
                      </p>
                    </Link>
                  ))}
                </div>
              ) : (
                <div className="text-center py-4">
                  <p className="text-muted mb-0">No lessons created yet.</p>
                  <Link to="/lessons/new" className="btn btn-primary mt-2">
                    Create your first lesson
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
