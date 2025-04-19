import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const LessonList = () => {
  const [lessons, setLessons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState({
    gradeLevel: '',
    strategy: ''
  });
  const [deleteId, setDeleteId] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);

  // Fetch lessons on component mount
  useEffect(() => {
    const fetchLessons = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/lessons');
        setLessons(response.data);
      } catch (err) {
        setError('Failed to load lessons. Please try again later.');
        console.error('Error fetching lessons:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchLessons();
  }, []);

  // Handle search input change
  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  // Handle filter changes
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilter(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Filter and search lessons
  const filteredLessons = lessons.filter(lesson => {
    // Apply search term filter
    const matchesSearch = lesson.topic.toLowerCase().includes(searchTerm.toLowerCase());
    
    // Apply grade level filter if selected
    const matchesGrade = filter.gradeLevel ? lesson.grade_level === filter.gradeLevel : true;
    
    // Apply strategy filter if selected
    const matchesStrategy = filter.strategy ? lesson.teaching_strategy === filter.strategy : true;
    
    return matchesSearch && matchesGrade && matchesStrategy;
  });

  // Format date for display
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  // Open delete confirmation modal
  const openDeleteModal = (id) => {
    setDeleteId(id);
    setShowDeleteModal(true);
  };

  // Close delete confirmation modal
  const closeDeleteModal = () => {
    setShowDeleteModal(false);
    setDeleteId(null);
  };

  // Handle lesson deletion
  const handleDeleteLesson = async () => {
    if (!deleteId) return;
    
    try {
      setDeleteLoading(true);
      await axios.delete(`/api/lessons/${deleteId}`);
      
      // Remove deleted lesson from state
      setLessons(prev => prev.filter(lesson => lesson.id !== deleteId));
      
      // Close modal
      closeDeleteModal();
    } catch (err) {
      setError('Failed to delete lesson. Please try again later.');
      console.error('Error deleting lesson:', err);
    } finally {
      setDeleteLoading(false);
    }
  };

  // Grade level options for filter
  const gradeOptions = [
    { value: 'K', label: 'Kindergarten' },
    { value: '1', label: '1st Grade' },
    { value: '2', label: '2nd Grade' },
    { value: '3', label: '3rd Grade' },
    { value: '4', label: '4th Grade' },
    { value: '5', label: '5th Grade' },
    { value: '6', label: '6th Grade' },
    { value: '7', label: '7th Grade' },
    { value: '8', label: '8th Grade' },
    { value: '9', label: '9th Grade' },
    { value: '10', label: '10th Grade' },
    { value: '11', label: '11th Grade' },
    { value: '12', label: '12th Grade' }
  ];

  // Teaching strategy options for filter
  const strategyOptions = [
    { value: 'cooperative_learning', label: 'Cooperative Learning' },
    { value: 'brainstorming', label: 'Brainstorming' },
    { value: 'discovery_learning', label: 'Discovery Learning' },
    { value: 'direct_instruction', label: 'Direct Instruction' },
    { value: 'project_based', label: 'Project-Based Learning' },
    { value: 'flipped_classroom', label: 'Flipped Classroom' },
    { value: 'inquiry_based', label: 'Inquiry-Based Learning' },
    { value: 'differentiated_instruction', label: 'Differentiated Instruction' },
    { value: 'game_based', label: 'Game-Based Learning' }
  ];

  // Determine content based on loading and data state
  let content;
  
  if (loading) {
    content = (
      <div className="text-center py-5">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  } else if (error) {
    content = (
      <div className="alert alert-danger" role="alert">
        {error}
      </div>
    );
  } else if (filteredLessons.length === 0) {
    content = (
      <div className="text-center py-5">
        <p className="text-muted mb-3">
          {lessons.length === 0 
            ? "You haven't created any lesson plans yet." 
            : "No lessons match your search criteria."}
        </p>
        {lessons.length === 0 && (
          <Link to="/lessons/new" className="btn btn-primary">
            Create Your First Lesson
          </Link>
        )}
      </div>
    );
  } else {
    content = (
      <div className="table-responsive">
        <table className="table table-hover align-middle">
          <thead>
            <tr>
              <th>Topic</th>
              <th>Grade</th>
              <th>Strategy</th>
              <th>Created</th>
              <th>Modified</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredLessons.map(lesson => (
              <tr key={lesson.id}>
                <td>
                  <Link to={`/lessons/${lesson.id}`} className="text-decoration-none">
                    {lesson.topic}
                  </Link>
                </td>
                <td>{lesson.grade_level}</td>
                <td>
                  {strategyOptions.find(s => s.value === lesson.teaching_strategy)?.label || 
                   lesson.teaching_strategy.replace('_', ' ')}
                </td>
                <td>{formatDate(lesson.date_created)}</td>
                <td>{formatDate(lesson.date_modified)}</td>
                <td>
                  <div className="btn-group btn-group-sm">
                    <Link 
                      to={`/lessons/${lesson.id}`} 
                      className="btn btn-outline-primary"
                      title="View"
                    >
                      <i className="bi bi-eye"></i>
                    </Link>
                    <Link 
                      to={`/lessons/${lesson.id}/edit`} 
                      className="btn btn-outline-secondary"
                      title="Edit"
                    >
                      <i className="bi bi-pencil"></i>
                    </Link>
                    <button 
                      className="btn btn-outline-danger"
                      onClick={() => openDeleteModal(lesson.id)}
                      title="Delete"
                    >
                      <i className="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  return (
    <div className="lessons-list">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>My Lesson Plans</h2>
        <Link to="/lessons/new" className="btn btn-primary">
          <i className="bi bi-plus-circle me-1"></i> New Lesson
        </Link>
      </div>
      
      <div className="card shadow-sm mb-4">
        <div className="card-body">
          <div className="row g-3">
            <div className="col-md-6">
              <input
                type="text"
                className="form-control"
                placeholder="Search by topic..."
                value={searchTerm}
                onChange={handleSearchChange}
              />
            </div>
            <div className="col-md-3">
              <select
                className="form-select"
                name="gradeLevel"
                value={filter.gradeLevel}
                onChange={handleFilterChange}
              >
                <option value="">All Grades</option>
                {gradeOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="col-md-3">
              <select
                className="form-select"
                name="strategy"
                value={filter.strategy}
                onChange={handleFilterChange}
              >
                <option value="">All Strategies</option>
                {strategyOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>
      
      <div className="card shadow-sm">
        <div className="card-body">
          {content}
        </div>
      </div>
      
      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="modal fade show" style={{ display: 'block' }} tabIndex="-1">
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Confirm Deletion</h5>
                <button type="button" className="btn-close" onClick={closeDeleteModal}></button>
              </div>
              <div className="modal-body">
                <p>Are you sure you want to delete this lesson plan? This action cannot be undone.</p>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={closeDeleteModal}
                  disabled={deleteLoading}
                >
                  Cancel
                </button>
                <button 
                  type="button" 
                  className="btn btn-danger" 
                  onClick={handleDeleteLesson}
                  disabled={deleteLoading}
                >
                  {deleteLoading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Deleting...
                    </>
                  ) : 'Delete'}
                </button>
              </div>
            </div>
          </div>
          <div className="modal-backdrop fade show"></div>
        </div>
      )}
    </div>
  );
};

export default LessonList;
