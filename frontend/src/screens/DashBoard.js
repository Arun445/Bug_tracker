import React from "react";
import SideBar from "../components/SideBar";

function DashBoard() {
  return (
    <div className="main-container">
      <div>
        <SideBar />
      </div>
      <div className="main">
        <h2>Dashboard</h2>
        <div className="dashboard">
          <div className="dashboard-box"></div>

          <div className="dashboard-box-sm"></div>
          <div className="dashboard-box-sm"></div>
          <div className="dashboard-box-sm"></div>
        </div>
      </div>
    </div>
  );
}

export default DashBoard;
