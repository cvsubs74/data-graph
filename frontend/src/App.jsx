import { useState, useRef } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import './App.css';

// IMPORTANT: Replace with your actual Cloud Function URLs
const INGEST_URL = 'https://ingest-function-pt7snlxyuq-uc.a.run.app'; // Replace with your Ingest Function URL
const QUERY_URL = 'https://query-function-pt7snlxyuq-uc.a.run.app';   // Replace with your Query Function URL

function App() {
  const [files, setFiles] = useState([]);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState({});
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const chosenFiles = Array.from(event.target.files);
    setFiles(chosenFiles);
    setUploadStatus({});
  };

  const handleFileUpload = async () => {
    if (files.length === 0) {
      alert('Please select files to upload.');
      return;
    }

    setIsLoading(true);
    const newStatus = {};

    for (const file of files) {
      const formData = new FormData();
      formData.append('file', file);

      try {
        await axios.post(INGEST_URL, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        newStatus[file.name] = '✅ Uploaded';
      } catch (error) {
        console.error(`Error uploading ${file.name}:`, error);
        newStatus[file.name] = `❌ Error: ${error.response?.data?.error || error.message}`;
      }
      setUploadStatus(prevStatus => ({ ...prevStatus, ...newStatus }));
    }

    setIsLoading(false);
  };

  const handleQuery = async () => {
    if (!question) {
      alert('Please enter a question.');
      return;
    }

    setIsLoading(true);
    setAnswer('');

    try {
      const response = await axios.post(QUERY_URL, { question });
      // The backend now returns a JSON object like { "answer": "..." }
      setAnswer(response.data.answer || response.data);
    } catch (error) {
      console.error('Error asking question:', error);
      const errorMessage = error.response?.data?.error || error.message;
      setAnswer(`**Error:** ${errorMessage}`);
    }

    setIsLoading(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Serverless Graph RAG</h1>
      </header>
      <main>
        <div className="card">
          <h2>Step 1: Ingest Documents</h2>
          <input type="file" multiple onChange={handleFileChange} ref={fileInputRef} style={{ display: 'none' }} />
          <button onClick={() => fileInputRef.current.click()}>
            Select Files
          </button>
          {files.length > 0 && (
            <div className="file-list">
              <h4>Selected files:</h4>
              <ul>
                {files.map((file, index) => (
                  <li key={index}>{file.name} {uploadStatus[file.name]}</li>
                ))}
              </ul>
            </div>
          )}
          <button onClick={handleFileUpload} disabled={isLoading || files.length === 0}>
            {isLoading ? 'Uploading...' : 'Upload to Knowledge Graph'}
          </button>
        </div>

        <div className="card">
          <h2>Step 2: Ask a Question</h2>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g., What is the data breach notification process?"
            rows={4}
          />
          <button onClick={handleQuery} disabled={isLoading || !question}>
            {isLoading ? 'Thinking...' : 'Ask'}
          </button>
          {answer && (
            <div className="answer-container">
              <h3>Answer:</h3>
              <div className="answer-text">
                <ReactMarkdown>{answer}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
