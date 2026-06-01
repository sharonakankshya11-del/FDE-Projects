import React, { useState } from "react";
import UploadPage from "./pages/UploadPage";
import DashboardPage from "./pages/DashboardPage";
import ChatPage from "./pages/ChatPage";
import ReportPage from "./pages/ReportPage";
import Sidebar from "./components/Sidebar";
import "./App.css";

export default function App() {
  const [activePage, setActivePage] = useState("upload");
  const [analysisData, setAnalysisData] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  return (
    <div className="app-shell">
      <Sidebar
        activePage={activePage}
        onNavigate={setActivePage}
        hasData={!!analysisData}
      />
      <main className="main-content">
        {activePage === "upload" && (
          <UploadPage
            onAnalysisComplete={(data) => {
              setAnalysisData(data);
              setActivePage("dashboard");
            }}
            isAnalyzing={isAnalyzing}
            setIsAnalyzing={setIsAnalyzing}
          />
        )}
        {activePage === "dashboard" && (
          <DashboardPage data={analysisData} onNavigate={setActivePage} />
        )}
        {activePage === "chat" && (
          <ChatPage analysisData={analysisData} />
        )}
        {activePage === "report" && (
          <ReportPage analysisData={analysisData} />
        )}
      </main>
    </div>
  );
}
