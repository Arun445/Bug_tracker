import React, { useState } from "react";

function SideBar() {
  const [open, setOpen] = useState(true);

  return (
    <nav>
      <div className={!open ? "sidebar" : "sidebar active"}>
        <div className="sidebar-open" onClick={() => setOpen(!open)}>
          {open ? (
            <i className="fas fa-angle-left"></i>
          ) : (
            <i className="fas fa-angle-right"></i>
          )}
        </div>
        <ul>
          <li>
            <a href="#">
              <i className="fas fa-columns"></i>Dashboard
            </a>
          </li>
          <li>
            <a href="#">
              <i className="fas fa-clipboard-list"></i>My Tickets
            </a>
          </li>
          <li>
            <a href="#">
              <i className="fas fa-tasks"></i>Projects
            </a>
          </li>
          <li>
            <a href="#">
              <i className="fas fa-users"></i>Users
            </a>
          </li>
        </ul>
      </div>
    </nav>
  );
}

export default SideBar;
