import React, { useState } from "react";
import onClickOutside from "react-onclickoutside";

function DropDown() {
  const [open, setOpen] = useState(false);

  DropDown.handleClickOutside = () => setOpen(false);
  return (
    <div>
      <a href="#" className="nav-user" onClick={() => setOpen(!open)}>
        bazinga<i className="fas fa-chevron-down"></i>
      </a>
      {open && (
        <div className="nav-dropdown">
          <a href="#" className="dropdown-item">
            logout
          </a>
          <a href="#" className="dropdown-item">
            profile
          </a>
        </div>
      )}
    </div>
  );
}
const clickOutsideConfig = {
  handleClickOutside: () => DropDown.handleClickOutside,
};
export default onClickOutside(DropDown, clickOutsideConfig);
