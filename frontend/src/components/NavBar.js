import React from "react";
import logo from "../logo.svg";
function NavBar() {
  return (
    <div className="nav-container">
      <header>
        <div className="nav-logo">
          <img src={logo} className="svg-logo" />
          <a>Bug Tracker</a>
        </div>
        <ul className="nav-right">
          <li>
            <form>
              <input />
              <button>
                <i className="fas fa-search"></i>
              </button>
            </form>
          </li>
          <li>
            <button className="nav-bell-btn">
              <i className="far fa-bell nav-bell-svg"></i>
              <i className="nav-bell-notification">2</i>
            </button>
          </li>
          <li>
            <a href="#">
              bazinga<i className="fas fa-chevron-down"></i>
            </a>
            <div className="nav-dropdown">
              <ul>
                <li>logout</li>
                <li>profile</li>
              </ul>
            </div>
          </li>
        </ul>
      </header>
    </div>
  );
}

export default NavBar;
