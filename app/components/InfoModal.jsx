import React from "react";


const InfoModal = ({ isOpen, content, onClose }) => {
  if (!isOpen) return null;

  return (
    <dialog className="modal modal-bottom sm:modal-middle" open={isOpen}>
      <div className="modal-box" style={{ whiteSpace: "pre-wrap" }}>
        <h3 className="font-bold text-lg">Info</h3>
        <p className="py-4">{content}</p>
        <div className="modal-action">
          <button className="btn" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </dialog>
  );
};

export default InfoModal;
