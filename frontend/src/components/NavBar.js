import React, { useState } from "react";
import { ReactComponent as BugLogo } from "../logo.svg";
import DropDown from "./DropDown";
function NavBar(props) {
  return (
    <div className="nav-container">
      <header>
        <div className="nav-logo">
          <a className="svg-logo">{<BugLogo />}</a>
          <a>Bug Tracker</a>
        </div>
        <ul className="nav-nav">
          <li>
            <form className="nav-form">
              <input className="nav-input" />
              <button className="search-btn">
                <i className="fas fa-search"></i>
              </button>
            </form>
            <button className="nav-bell-btn">
              <i className="far fa-bell nav-bell-svg"></i>
              <i className="nav-bell-notification">2</i>
            </button>
          </li>

          <li>
            <DropDown />
          </li>
        </ul>
      </header>
    </div>
  );
}

export default NavBar;
