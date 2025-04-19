import React, { useState, useEffect } from 'react';
import { useHistory, useParams } from 'react-router-dom';
import axios from 'axios';

const LessonForm = () => {
  const { id } = useParams();
  const history = useHistory();
  const isEditing = !!id;

  const [formData, setFormData] = useState({
    grade_level: '',
    topic: '',
    teaching_strategy: ''
  });
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [lesson, setLesson] = useState(null);

  // Grade level options
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

  // Teaching strategy options
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

  // Fetch lesson data if editing
  useEffect(() => {
    if (isEditing) {
      const fetchLesson = async () => {
        try {
          setLoading(true);
          const response = await axios.get(`/api/lessons/${id}`);
          setLesson(response.data);
          setFormData({
            grade_level: response.data.grade_level,
            topic: response.data.topic,
            teaching_strategy: response.data.teaching_strategy
          });
        } catch (err) {
          setError('Failed to load lesson. Please try again later.');
          console.error('Error fetching lesson:', err);
        } finally {
          setLoading(false);
        }
      };

      fetchLesson();
    }
  }, [id, isEditing]);

  // Handle form input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!formData.grade_level || !formData.topic || !formData.teaching_strategy) {
      setError('Please fill out all fields');
      return;
    }
    
    try {
      setGenerating(true);
      setError(null);
      
      if (isEditing) {
        // Update existing lesson
        await axios.put(`/api/lessons/${id}`, formData);
        history.push(`/lessons/${id}`);
      } else {
        // Create new lesson
        const response = await axios.post('/api/lessons', formData);
        history.push(`/lessons/${response.data.lesson.id}`);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'An error occurred. Please try again.');
      console.error('Error saving lesson:', err);
    } finally {
      setGenerating(false);
    }
  };

  // Handle cancel
  const handleCancel = () => {
    if (isEditing) {
      history.push(`/lessons/${id}`);
    } else {
      history.push('/lessons');
    }
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

  return (
    <div className="row justify-content-center">
      <div className="col-md-8">
        <div className="card shadow-sm">
          <div className="card-body p-4">
            <h2 className="text-center mb-4">
              {isEditing ? 'Edit Lesson Plan' : 'Create New Lesson Plan'}
            </h2>
            
            {error && (
              <div className="alert alert-danger" role="alert">
                {error}
              </div>
            )}
            
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label htmlFor="grade_level" className="form-label">Grade Level</label>
                <select
                  className="form-select"
                  id="grade_level"
                  name="grade_level"
                  value={formData.grade_level}
                  onChange={handleChange}
                  required
                >
                  <option value="" disabled>Select grade level</option>
                  {gradeOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="mb-3">
                <label htmlFor="topic" className="form-label">Lesson Topic</label>
                <input
                  type="text"
                  className="form-control"
                  id="topic"
                  name="topic"
                  value={formData.topic}
                  onChange={handleChange}
                  placeholder="e.g., Photosynthesis, American Revolution, Fractions"
                  required
                />
              </div>
              
              <div className="mb-3">
                <label htmlFor="teaching_strategy" className="form-label">Teaching Strategy</label>
                <select
                  className="form-select"
                  id="teaching_strategy"
                  name="teaching_strategy"
                  value={formData.teaching_strategy}
                  onChange={handleChange}
                  required
                >
                  <option value="" disabled>Select teaching strategy</option>
                  {strategyOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="d-grid gap-2 d-md-flex justify-content-md-end mt-4">
                <button 
                  type="button" 
                  className="btn btn-outline-secondary" 
                  onClick={handleCancel}
                  disabled={generating}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn btn-primary" 
                  disabled={generating}
                >
                  {generating ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      {isEditing ? 'Updating...' : 'Generating...'}
                    </>
                  ) : (
                    isEditing ? 'Update Lesson Plan' : 'Generate Lesson Plan'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
        
        {!isEditing && (
          <div className="card mt-4 shadow-sm">
            <div className="card-body">
              <h5 className="card-title">How It Works</h5>
              <ol className="mb-0">
                <li>Select the grade level appropriate for your students</li>
                <li>Enter your specific lesson topic</li>
                <li>Choose a teaching strategy that suits your classroom needs</li>
                <li>Click "Generate Lesson Plan" to create your customized lesson</li>
                <li>Review, edit, and download your lesson and presentation</li>
              </ol>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LessonForm;
