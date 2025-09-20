import React, { useState, useEffect } from "react";
import "./App.css";
import { Bell, LogOut, ChevronLeft, ChevronRight } from "lucide-react"; // add at top with imports

import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [user, setUser] = useState(null);
  const [email, setEmail] = useState("");
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [question, setQuestion] = useState("");
  const [language, setLanguage] = useState("english");
  const [overallLanguage, setOverallLanguage] = useState("english");
  const [chatHistory, setChatHistory] = useState([]);
  const [asking, setAsking] = useState(false);
  const [currentSummary, setCurrentSummary] = useState(null);
  const [tone, setTone] = useState("professional"); // New tone state
  

  const languageOptions = {
    english: "English",
    hindi: "हिंदी",
    punjabi: "ਪੰਜਾਬੀ",
  };

  const toneOptions = {
    professional: "Professional",
    friendly: "Friendly",
    casual: "Casual",
  };

  // Login
  const handleLogin = async () => {
    if (!email) return;
    try {
      const response = await axios.post(`${API}/users`, { email });
      setUser(response.data);
      loadUserDocuments(response.data.id);
    } catch (error) {
      console.error("Error creating/getting user:", error);
    }
  };

  // Load user documents
  const loadUserDocuments = async (userId) => {
    try {
      const response = await axios.get(`${API}/documents/${userId}`);
      setDocuments(response.data);
    } catch (error) {
      console.error("Error loading documents:", error);
    }
  };

  // Upload file
  const handleUpload = async () => {
    if (!uploadFile || !user) return;

    const formData = new FormData();
    formData.append("file", uploadFile);
    formData.append("user_id", user.id);
    formData.append("tone", tone); // send tone to backend

    setUploading(true);
    try {
      const response = await axios.post(`${API}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      alert(`Document uploaded successfully! ${response.data.uploads_remaining} free uploads remaining.`);
      setUploadFile(null);
      loadUserDocuments(user.id);
    } catch (error) {
      if (error.response?.status === 402) {
        alert("Free uploads exceeded! ₹50 payment required for additional uploads.");
      } else {
        alert("Error uploading document: " + (error.response?.data?.detail || error.message));
      }
    }
    setUploading(false);
  };

  // Select document
  const selectDocument = async (doc) => {
    setSelectedDocument(doc);
    setCurrentSummary({
      english: doc.summary,
      hindi: doc.summary_hindi,
      punjabi: doc.summary_punjabi,
    });
    try {
      const response = await axios.get(`${API}/chat/${doc.id}/${user.id}`);
      setChatHistory(response.data);
    } catch {
      setChatHistory([]);
    }
  };

  // Ask question
  const handleAskQuestion = async () => {
    if (!question.trim() || !selectedDocument || !user) return;
    setAsking(true);
    try {
      const response = await axios.post(`${API}/chat`, {
        document_id: selectedDocument.id,
        user_id: user.id,
        question,
        language,
      });
      setChatHistory([...chatHistory, response.data]);
      setQuestion("");
    } catch (error) {
      alert("Error asking question: " + (error.response?.data?.detail || error.message));
    }
    setAsking(false);
  };

  // Download/View PDF
  const handleViewPDF = (doc) => {
    if (!doc.file_url) return;
    window.open(doc.file_url, "_blank");
  };

  // Copy summary
  const handleCopySummary = () => {
    if (!currentSummary) return;
    const text = currentSummary[language] || currentSummary.english;
    navigator.clipboard.writeText(text);
    alert("Summary copied to clipboard!");
  };

  // Share summary
  const handleShareSummary = () => {
    if (!currentSummary) return;
    const text = currentSummary[language] || currentSummary.english;
    if (navigator.share) {
      navigator.share({
        title: selectedDocument.filename,
        text,
      });
    } else {
      navigator.clipboard.writeText(text);
      alert("Summary copied to clipboard!");
    }
  };

  const reviews = [
    {
      text: "Amazing tool! Helped me summarize legal docs quickly.",
      author: "Priya S.",
      avatar: "https://randomuser.me/api/portraits/women/68.jpg",
    },
    {
      text: "Super easy to use and the summaries are spot on!",
      author: "Rajesh K.",
      avatar: "https://randomuser.me/api/portraits/men/32.jpg",
    },
    {
      text: "Saved me hours of reading through contracts.",
      author: "Ananya M.",
      avatar: "https://randomuser.me/api/portraits/women/45.jpg",
    },
    {
      text: "The Q&A feature is a game changer!",
      author: "Vivek R.",
      avatar: "https://randomuser.me/api/portraits/men/22.jpg",
    },
    {
      text: "Highly recommend for all legal professionals.",
      author: "Karan P.",
      avatar: "https://randomuser.me/api/portraits/men/46.jpg",
    },
  ];

  const [activeIndex, setActiveIndex] = useState(0);
   useEffect(() => {
    const interval = setInterval(() => {
      setActiveIndex((prev) =>
        prev === reviews.length - 1 ? 0 : prev + 1
      );
    }, 5000);

    return () => clearInterval(interval); // cleanup
  }, [reviews.length]);
   const prevSlide = () => {
    setActiveIndex((p) => (p === 0 ? reviews.length - 1 : p - 1));
  };

  const nextSlide = () => {
    setActiveIndex((p) => (p === reviews.length - 1 ? 0 : p + 1));
  };



  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center p-4">
        <div className="bg-white/15 backdrop-blur-lg rounded-2xl p-8 w-full max-w-md border border-white/20">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-white mb-2">Case-AI</h1>
            <p className="text-blue-200">Your Legal Document Assistant</p>
          </div>
          <div className="space-y-4">
            <input
              type="email"
              placeholder="Enter your email to continue"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 text-white placeholder-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400"
              onKeyPress={(e) => e.key === "Enter" && handleLogin()}
            />
            <button
              onClick={handleLogin}
              className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
            >
              Get Started
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex flex-col">
     <div className="fixed top-0 left-0 right-0 z-50 bg-white/15 backdrop-blur-lg border-b border-white/20 p-4 flex justify-between items-center">
  {/* Left - Logo */}
  <div>
    <h1 className="text-2xl font-bold text-white">Case Ai</h1>
    <p className="text-blue-100">Welcome, {user.email}</p>
  </div>

  {/* Right - Actions */}
  <div className="flex items-center space-x-4 text-white">
    <p className="text-sm">Uploads Used: {user.uploads_used}/2 free</p>
    {user.uploads_used >= 2 && <p className="text-yellow-300 text-sm">₹50/upload extra</p>}

    <select
      value={overallLanguage}
      onChange={(e) => setOverallLanguage(e.target.value)}
      className="px-2 py-1 rounded-lg bg-white/10 border border-white/20 text-white focus:outline-none"
    >
      {Object.entries(languageOptions).map(([lang, label]) => (
        <option key={lang} value={lang} className="bg-gray-800">
          {label}
        </option>
      ))}
    </select>

    <button className="relative p-2 rounded-lg hover:bg-white/10 transition-colors">
      <Bell className="w-5 h-5 text-white" />
      <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
    </button>

    <button
      onClick={() => setUser(null)}
      className="flex items-center px-3 py-1 rounded-lg bg-white/15 border border-white/20 text-white focus:outline-none"
    >
      <LogOut className="w-4 h-4 mr-1" />
      Logout
    </button>
  </div>
</div>

<br/><br/><br/><br/>

      <div className="flex-1 max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Panel */}
        <div className="space-y-6">
          <div className="bg-white/15 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <h2 className="text-xl font-semibold text-white mb-4">Upload Document</h2>
            <div className="space-y-4">
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setUploadFile(e.target.files[0])}
                className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/20 text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-blue-600 file:text-white file:cursor-pointer"
              />
              <div className="flex items-center space-x-2">
                <label className="text-white">Tone:</label>
                <select
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                  className="px-2 py-1 rounded-lg bg-white/10 border border-white/20 text-white"
                >
                  {Object.entries(toneOptions).map(([key, label]) => (
                    <option key={key} value={key} className="bg-gray-800">{label}</option>
                  ))}
                </select>
              </div>
              <button
                onClick={handleUpload}
                disabled={!uploadFile || uploading}
                className="w-full py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
              >
                {uploading ? "Uploading & Analyzing..." : "Upload PDF"}
              </button>
              <p className="text-sm text-blue-100">First 2 uploads free, then ₹50 per document</p>
            </div>
          </div>

          {/* Documents List */}
<div className="bg-white/15 backdrop-blur-lg rounded-xl p-6 border border-white/20">
  <h2 className="text-xl font-semibold text-white mb-4">Your Documents</h2>
  <div className="space-y-2 max-h-96 overflow-y-auto">
    {documents.map((doc) => (
      <div
        key={doc.id}
        className={`p-3 rounded-lg border cursor-pointer flex flex-col transition-colors ${
          selectedDocument?.id === doc.id
            ? "bg-blue-600/30 border-blue-400"
            : "bg-white/5 border-white/10 hover:bg-white/10"
        }`}
      >
        <div className="flex justify-between items-center mb-2">
          <div onClick={() => selectDocument(doc)}>
            <p className="text-white font-medium truncate">{doc.filename}</p>
            <p className="text-blue-200 text-sm">{new Date(doc.upload_date).toLocaleDateString()}</p>
          </div>
          <button
            onClick={() => handleViewPDF(doc)}
            className="px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm"
          >
            Download
          </button>
        </div>
        {/* Display Tone for each document */}
        <p className="text-yellow-300 text-sm mt-1">
          Tone: {toneOptions[tone] || "Professional"}
        </p>
      </div>
    ))}
  </div>
</div>

        </div>

        {/* Middle Panel - Summary */}
        <div className="bg-white/15 backdrop-blur-lg rounded-xl p-6 border border-white/20">
          <h2 className="text-xl font-semibold text-white mb-4">Document Summary</h2>
          {selectedDocument && currentSummary ? (
            <div className="space-y-4">
              <div className="flex space-x-2 mb-4">
                {Object.entries(languageOptions).map(([lang, label]) => (
                  <button
                    key={lang}
                    onClick={() => setLanguage(lang)}
                    className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                      language === lang
                        ? "bg-blue-600 text-white"
                        : "bg-white/10 text-blue-200 hover:bg-white/20"
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
              <div className="bg-white/5 rounded-lg p-4 max-h-96 overflow-y-auto">
                <p className="text-white whitespace-pre-wrap">
                  {language === "english" && currentSummary.english}
                  {language === "hindi" && currentSummary.hindi}
                  {language === "punjabi" && currentSummary.punjabi}
                </p>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={handleCopySummary}
                  className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm"
                >
                  Copy
                </button>
                <button
                  onClick={handleShareSummary}
                  className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm"
                >
                  Share
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center text-blue-200 py-12">
              <p>Select a document to view its summary</p>
            </div>
          )}
        </div>

        {/* Right Panel - Q&A */}
        <div className="bg-white/15 backdrop-blur-lg rounded-xl p-6 border border-white/20">
          <h2 className="text-xl font-semibold text-white mb-4">Ask Questions</h2>
          {selectedDocument ? (
            <div className="space-y-4">
              <div className="bg-white/5 rounded-lg p-4 h-64 overflow-y-auto space-y-3">
                {chatHistory.length === 0 ? (
                  <p className="text-blue-200 text-center py-8">Ask questions about the document</p>
                ) : (
                  chatHistory.map((chat) => (
                    <div key={chat.id} className="space-y-2">
                      <div className="bg-blue-600/20 rounded-lg p-3">
                        <p className="text-white font-medium">Q: {chat.question}</p>
                      </div>
                      <div className="bg-green-600/20 rounded-lg p-3">
                        <p className="text-white">A: {chat.answer}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>

              <div className="space-y-3">
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/20 text-white focus:outline-none focus:ring-2 focus:ring-blue-400"
                >
                  {Object.entries(languageOptions).map(([lang, label]) => (
                    <option key={lang} value={lang} className="bg-gray-800">
                      {label}
                    </option>
                  ))}
                </select>

                <textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Ask a question about the document..."
                  className="w-full px-3 py-2 rounded-lg bg-white/10 border border-white/20 text-white placeholder-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
                  rows="3"
                />

                <button
                  onClick={handleAskQuestion}
                  disabled={!question.trim() || asking}
                  className="w-full py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
                >
                  {asking ? "Getting Answer..." : "Ask Question"}
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center text-blue-200 py-12">
              <p>Select a document to start asking questions</p>
            </div>
          )}
        </div>
      </div>
    <div className="bg-white/15 backdrop-blur-lg rounded-xl p-6 border border-white/20 max-w-7xl mx-auto mt-6 w-full">
  <h2 className="text-xl font-semibold text-white mb-4">Pricing & Advantages</h2>
  <table className="w-full text-white border border-white/20 mb-4">
    <thead>
      <tr className="border-b border-white/20">
        <th className="px-3 py-2 text-left">Plan</th>
        <th className="px-3 py-2 text-left">Price</th>
        <th className="px-3 py-2 text-left">Advantages</th>
      </tr>
    </thead>
    <tbody>
      <tr className="border-b border-white/20">
        <td className="px-3 py-2">Free</td>
        <td className="px-3 py-2">₹0</td>
        <td className="px-3 py-2">2 uploads per week, Basic Summaries</td>
      </tr>
      <tr className="border-b border-white/20">
        <td className="px-3 py-2">Pro</td>
        <td className="px-3 py-2">₹50/upload</td>
        <td className="px-3 py-2">Unlimited uploads, Multi-language summaries, Q&A</td>
      </tr>
    </tbody>
  </table>
</div>

{/* Reviews Carousel */}
     <div className="bg-white/15 backdrop-blur-lg rounded-xl p-6 border border-white/20 max-w-7xl mx-auto mt-6 w-full relative">
      <h2 className="text-xl font-semibold text-white mb-6 text-center">
        What people think Case Ai?
      </h2>

      <div className="flex items-center justify-center gap-4">
        {/* Prev */}
        <button
          onClick={prevSlide}
          aria-label="Previous review"
          className="p-2 rounded-full bg-white/20 hover:bg-white/30 text-white transition"
        >
          <ChevronLeft size={20} />
        </button>

        {/* Single active card */}
        <div className="w-full max-w-[720px] h-56 flex items-center justify-center overflow-hidden">
          <div
            key={activeIndex}
            className="w-full max-w-[560px] mx-auto p-6 rounded-lg flex flex-col items-center text-center
                       transition-all duration-700 ease-in-out transform scale-105"
          >
            <div className="bg-white/20 rounded-lg p-6 shadow-xl flex flex-col items-center ">
              <img
                src={reviews[activeIndex].avatar}
                alt={reviews[activeIndex].author}
                className="w-20 h-20 rounded-full border-2 border-white mb-4 object-cover"
              />
              <p className="text-white mb-3 italic text-lg leading-relaxed">
                "{reviews[activeIndex].text}"
              </p>
              <p className="text-blue-200 text-sm font-semibold">
                — {reviews[activeIndex].author}
              </p>
            </div>
          </div>
        </div>

        {/* Next */}
        <button
          onClick={nextSlide}
          aria-label="Next review"
          className="p-2 rounded-full bg-white/20 hover:bg-white/30 text-white transition"
        >
          <ChevronRight size={20} />
        </button>
      </div>
    </div>
      {/* Footer */}
<footer className="bg-white/15 backdrop-blur-lg border-t border-white/20 py-4 mt-6">
  <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row justify-between items-center text-sm text-blue-100">
    <p>© {new Date().getFullYear()} Case-AI. All rights reserved.</p>
    <div className="flex space-x-4 mt-2 sm:mt-0">
      <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
      <a href="#" className="hover:text-white transition-colors">Terms</a>
      <a href="#" className="hover:text-white transition-colors">Contact</a>
    </div>
  </div>
</footer>

    </div>
  );
}

export default App;
