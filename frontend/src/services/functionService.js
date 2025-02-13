import axios from "axios";
const API_URL = process.env.REACT_APP_API_URL;

export const functionService = {
  // Convert slides to video
  convertToVideo: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(
        `${API_URL}/api/v1/converter/slide-to-video`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          responseType: 'blob', // For downloading the video file
        }
      );
      
      // Create download link for video
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `lecture_${Date.now()}.mp4`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      return 'Video conversion completed! The download should start automatically.';
    } catch (error) {
      throw new Error('Failed to convert slides to video');
    }
  },

  // Generate quiz from materials
  generateQuiz: async (message, settings) => {
    try {
      // Return sample quiz for testing
      return {
        questions: [
          {
            question: "What is the primary purpose of machine learning?",
            options: [
              "To create human-like robots",
              "To enable computers to learn from data without explicit programming",
              "To replace all human jobs",
              "To store large amounts of data"
            ],
            correctAnswer: 1,
            explanation: "Machine learning is focused on developing algorithms that allow computers to learn patterns from data and make decisions without being explicitly programmed for each scenario."
          },
          {
            question: "Which of the following is NOT a type of machine learning?",
            options: [
              "Supervised Learning",
              "Unsupervised Learning",
              "Cognitive Learning",
              "Reinforcement Learning"
            ],
            correctAnswer: 2,
            explanation: "The main types of machine learning are Supervised Learning, Unsupervised Learning, and Reinforcement Learning. Cognitive Learning is not a standard category of machine learning."
          },
          {
            question: "What is overfitting in machine learning?",
            options: [
              "When a model performs poorly on training data",
              "When a model is too simple to learn patterns",
              "When a model learns noise in training data and performs poorly on new data",
              "When a model takes too long to train"
            ],
            correctAnswer: 2,
            explanation: "Overfitting occurs when a model learns the training data too well, including noise and outliers, which leads to poor generalization on new, unseen data."
          },
          {
            question: "Which algorithm is commonly used for classification problems?",
            options: [
              "Linear Regression",
              "K-means Clustering",
              "Logistic Regression",
              "Principal Component Analysis"
            ],
            correctAnswer: 2,
            explanation: "Logistic Regression is specifically designed for classification problems, where the output is categorical (e.g., yes/no, true/false)."
          },
          {
            question: "What is the purpose of the training dataset in machine learning?",
            options: [
              "To test the final model performance",
              "To validate model hyperparameters",
              "To teach the model patterns and relationships",
              "To deploy the model in production"
            ],
            correctAnswer: 2,
            explanation: "The training dataset is used to teach the model by allowing it to learn patterns and relationships from labeled examples. This is the data the model uses to adjust its parameters during the learning process."
          }
        ]
      };
    } catch (error) {
      throw new Error('Failed to generate quiz');
    }
  },

  // Process document for tutoring
  processTutoringDocument: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(
        `${API_URL}/api/v1/chat/process-document`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      
      return response.data;
    } catch (error) {
      throw new Error('Failed to process document');
    }
  }
}; 