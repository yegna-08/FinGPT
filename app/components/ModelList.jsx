"use client"
import React, { useState } from 'react';
import models from '@/models.json'; // Import the JSON data

function ModelList() {
  const [selectedModel, setSelectedModel] = useState(null);
//   const [modalInfo, setModalInfo] = useState({ isOpen: false, content: "" });

//   const openModal = (content) => {
//     setModalInfo({ isOpen: true, content });
//   };

//   const closeModal = () => {
//     setModalInfo({ isOpen: false, content: "" });
//   };

  return (
    <div>
      <div className="mt-20 p-4 overflow-x-auto border border-gray-300 rounded-lg">
        <table className="table w-full">
          {/* Table Head */}
          <thead>
            <tr className='text-white bg-purple-800'>
              <th>Name</th>
              <th>Author</th>
              <th>Publication Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          {/* Table Body */}
          <tbody>
            {models.map((model) => (
              <tr key={model.id}>
                <td>{model.name}</td>
                <td>{model.author}</td>
                <td>{model.publicationDate}</td>
                <td>
                  <button
                    className="btn btn-sm btn-outline btn-primary"
                    onClick={() => setSelectedModel(model)}
                  >
                    More info
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {selectedModel && (
        <div id="modal" className="modal modal-open">
        <div className="modal-box">
          <h3 className="font-bold text-lg">{selectedModel.name}</h3>
          <p className="py-4">{selectedModel.description}</p>
          <div className="modal-action">
            {selectedModel.links.paper && (
              <a href={selectedModel.links.paper} className="btn btn-accent" target="_blank" rel="noopener noreferrer">Paper</a>
            )}
            {selectedModel.links.code && (
              <a href={selectedModel.links.code} className="btn btn-accent" target="_blank" rel="noopener noreferrer">Model</a>
            )}
            {selectedModel.links.data && (
              <a href={selectedModel.links.data} className="btn btn-accent" target="_blank" rel="noopener noreferrer">Datasets</a>
            )}
            {selectedModel.links.leaderboard && (
              <a href={selectedModel.links.leaderboard} className="btn btn-accent" target="_blank" rel="noopener noreferrer">Leaderboard</a>
            )}
            <button className="btn" onClick={() => setSelectedModel(null)}>Close</button>
          </div>
        </div>
      </div>
      
      )}
    </div>
  );
}

export default ModelList;
