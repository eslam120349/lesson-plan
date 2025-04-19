import React, { useState, useEffect } from 'react';
import { useParams, useHistory, Link } from 'react-router-dom';
import axios from 'axios';
import { marked } from 'marked';

const LessonView = () => {
  const { id } = useParams();
  const history = useHistory();
  
  const [lesson, setLesson] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isGeneratingPPT, setIsGeneratingPPT] = useState(false);
  const [generationSuccess, setGenerationSuccess] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState('');

  // Fetch lesson data
  useEffect(() => {
    const fetchLesson = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`/api/lessons/${id}`);
        setLesson(response.data);
        setEditedContent(response.data.generated_plan || '');
      } catch (err) {
        setError('Failed to load lesson. Please try again later.');
        console.error('Error fetching lesson:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchLesson();
  }, [id]);

  // Generate PowerPoint presentation
  const generatePresentation = async () => {
    try {
      setIsGeneratingPPT(true);
      setGenerationSuccess(null);
      
      const response = await axios.post(`/api/lessons/${id}/presentation`);
      
      if (response.data.success) {
        setGenerationSuccess({
          message: response.data.message,
          presentationId: response.data.presentation_id
        });
        
        // Refresh lesson data to include new presentation
        const lessonResponse = await axios.get(`/api/lessons/${id}`);
        setLesson(lessonResponse.data);
      }
    } catch (err) {
      setError('Failed to generate presentation. Please try again later.');
      console.error('Error generating presentation:', err);
    } finally {
      setIsGeneratingPPT(false);
    }
  };

  // Download presentation
  const downloadPresentation = async (presentationId) => {
    try {
      window.open(`/api/presentations/${presentationId}/download`, '_blank');
    } catch (err) {
      setError('Failed to download presentation. Please try again later.');
      console.error('Error downloading presentation:', err);
    }
  };

  // Format date for display
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  // Toggle edit mode
  const toggleEditMode = () => {
    setIsEditing(!isEditing);
    if (!isEditing) {
      setEditedContent(lesson.generated_plan || '');
    }
  };

  // Handle content editing
  const handleContentChange = (e) => {
    setEditedContent(e.target.value);
  };

  // Save edited content
  const saveEditedContent = async () => {
    try {
      await axios.put(`/api/lessons/${id}`, {
        generated_plan: editedContent
      });
      
      // Update lesson state with edited content
      setLesson(prev => ({
        ...prev,
        generated_plan: editedContent
      }));
      
      // Exit edit mode
      setIsEditing(false);
      setGenerationSuccess({
        message: 'Lesson plan updated successfully.'
      });
    } catch (err) {
      setError('Failed to save changes. Please try again later.');
      console.error('Error saving changes:', err);
    }
  };

  // Cancel editing
  const cancelEditing = () => {
    setIsEditing(false);
    setEditedContent(lesson.generated_plan || '');
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

  if (!lesson) {
    return (
      <div className="alert alert-warning" role="alert">
        Lesson not found.
      </div>
    );
  }

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

  // Format strategy name for display
  const getStrategyLabel = (strategyValue) => {
    const strategy = strategyOptions.find(s => s.value === strategyValue);
    return strategy ? strategy.label : strategyValue.replace('_', ' ');
  };

  return (
    <div className="lesson-view">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>{lesson.topic}</h2>
        <div className="btn-group">
          <Link to="/lessons" className="btn btn-outline-secondary">
            <i className="bi bi-arrow-left me-1"></i> Back
          </Link>
          <Link to={`/lessons/${id}/edit`} className="btn btn-outline-primary">
            <i className="bi bi-pencil me-1"></i> Edit Details
          </Link>
        </div>
      </div>
      
      {generationSuccess && (
        <div className="alert alert-success alert-dismissible fade show" role="alert">
          {generationSuccess.message}
          <button 
            type="button" 
            className="btn-close" 
            onClick={() => setGenerationSuccess(null)}
          ></button>
        </div>
      )}
      
      <div className="row">
        <div className="col-md-8">
          <div className="card shadow-sm mb-4">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h5 className="mb-0">Lesson Plan</h5>
              <div>
                {isEditing ? (
                  <>
                    <button 
                      className="btn btn-sm btn-outline-secondary me-2" 
                      onClick={cancelEditing}
                    >
                      Cancel
                    </button>
                    <button 
                      className="btn btn-sm btn-success" 
                      onClick={saveEditedContent}
                    >
                      Save Changes
                    </button>
                  </>
                ) : (
                  <button 
                    className="btn btn-sm btn-outline-primary" 
                    onClick={toggleEditMode}
                  >
                    <i className="bi bi-pencil me-1"></i> Edit Content
                  </button>
                )}
              </div>
            </div>
            <div className="card-body">
              {isEditing ? (
                <textarea
                  className="form-control"
                  style={{ minHeight: '500px' }}
                  value={editedContent}
                  onChange={handleContentChange}
                ></textarea>
              ) : (
                <div 
                  className="lesson-content"
                  dangerouslySetInnerHTML={{ __html: marked(lesson.generated_plan || '') }}
                ></div>
              )}
            </div>
          </div>
        </div>
        
        <div className="col-md-4">
          <div className="card shadow-sm mb-4">
            <div className="card-header">
              <h5 className="mb-0">Lesson Details</h5>
            </div>
            <div className="card-body">
              <ul className="list-group list-group-flush">
                <li className="list-group-item d-flex justify-content-between">
                  <span className="fw-bold">Grade Level:</span>
                  <span>{lesson.grade_level}</span>
                </li>
                <li className="list-group-item d-flex justify-content-between">
                  <span className="fw-bold">Teaching Strategy:</span>
                  <span>{getStrategyLabel(lesson.teaching_strategy)}</span>
                </li>
                <li className="list-group-item d-flex justify-content-between">
                  <span className="fw-bold">Created:</span>
                  <span>{formatDate(lesson.date_created)}</span>
                </li>
                <li className="list-group-item d-flex justify-content-between">
                  <span className="fw-bold">Last Modified:</span>
                  <span>{formatDate(lesson.date_modified)}</span>
                </li>
              </ul>
            </div>
          </div>
          
          <div className="card shadow-sm mb-4">
            <div className="card-header">
              <h5 className="mb-0">PowerPoint Presentation</h5>
            </div>
            <div className="card-body">
              {lesson.presentations && lesson.presentations.length > 0 ? (
                <div>
                  <p>Presentations generated: {lesson.presentations.length}</p>
                  <div className="list-group">
                    {lesson.presentations.map(presentation => (
                      <div key={presentation.id} className="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                        <div>
                          <small className="text-muted d-block">
                            {formatDate(presentation.date_created)}
                          </small>
                          <span>Presentation #{presentation.id}</span>
                        </div>
                        <button
                          className="btn btn-sm btn-outline-primary"
                          onClick={() => downloadPresentation(presentation.id)}
                        >
                          <i className="bi bi-download me-1"></i> Download
                        </button>
                      </div>
                    ))}
                  </div>
                  <div className="d-grid mt-3">
                    <button 
                      className="btn btn-outline-primary"
                      onClick={generatePresentation}
                      disabled={isGeneratingPPT}
                    >
                      {isGeneratingPPT ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          Generating...
                        </>
                      ) : (
                        <>
                          <i className="bi bi-file-earmark-slides me-1"></i> Generate New Presentation
                        </>
                      )}
                    </button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-3">
                  <p className="mb-3">No presentations generated yet.</p>
                  <button 
                    className="btn btn-primary"
                    onClick={generatePresentation}
                    disabled={isGeneratingPPT}
                  >
                    {isGeneratingPPT ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        Generating...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-file-earmark-slides me-1"></i> Generate Presentation
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LessonView;
