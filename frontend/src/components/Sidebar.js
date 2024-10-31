// src/components/Sidebar.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { SquarePenIcon, PlusIcon } from './Icons'; // Custom icons

const Sidebar = () => {
  return (
    <aside className="top-0 z-50 flex h-screen w-64 flex-col overflow-auto bg-muted p-2">
      <div className="flex h-full flex-col">
        <div className="flex w-full items-center justify-between pb-2">
          <Link to="/search" className="flex h-9 items-center rounded-md px-2 hover:bg-border">
            <h1 className="text-2xl font-semibold">Happenstance</h1>
          </Link>
          <Link to="/search">
            <button className="inline-flex items-center justify-center rounded-md text-sm font-medium hover:bg-border h-9 w-9">
              <SquarePenIcon className="h-5 w-5" />
            </button>
          </Link>
        </div>
        {/* Connections Section */}
        <div className="mt-4">
          <p className="text-sm font-semibold px-2">Connections</p>
          <div className="space-y-2 px-2">
            {/* Example Connection */}
            <div className="flex justify-between items-center bg-muted p-2 rounded-md hover:bg-border transition">
              <div className="flex items-center space-x-2">
                <img src="/logos/gmail.svg" alt="Gmail" className="h-5 w-5" />
                <span className="text-sm font-medium opacity-75 hover:opacity-100">Active</span>
              </div>
              <div className="text-primary">
                {/* Check Icon */}
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
                  <path d="m9 12 2 2 4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
            </div>
            {/* Add more connections as needed */}
          </div>
        </div>
        {/* Intros Section */}
        <div className="mt-4">
          <p className="text-sm font-semibold px-2">Intros</p>
          <Link to="/intros" className="flex items-center justify-between px-2 py-1 text-sm font-medium text-muted-foreground hover:text-foreground transition">
            <span>View intros</span>
            {/* Chevron Icon */}
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 15 15" stroke="currentColor">
              <path d="M8.146 3.146a.5.5 0 011 0l4 4a.5.5 0 010 .708l-4 4a.5.5 0 01-.708-.708L11.793 8.5 7.438 4.146a.5.5 0 010-.708z" />
            </svg>
          </Link>
        </div>
        {/* Groups Section */}
        <div className="mt-4">
          <p className="text-sm font-semibold px-2">Groups</p>
          <Link to="/group" className="flex items-center justify-between px-2 py-1 text-sm font-medium text-muted-foreground hover:text-foreground transition">
            <span>Create group</span>
            {/* Chevron Icon */}
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 15 15" stroke="currentColor">
              <path d="M8.146 3.146a.5.5 0 011 0l4 4a.5.5 0 010 .708l-4 4a.5.5 0 01-.708-.708L11.793 8.5 7.438 4.146a.5.5 0 010-.708z" />
            </svg>
          </Link>
        </div>
        {/* Recents Section */}
        <div className="mt-4">
          <p className="text-sm font-semibold px-2">Recents</p>
          <div className="space-y-2 px-2">
            {/* Example Recent Search */}
            <Link to="/search/1c692f93-e4a7-4712-9ac0-a4a533b223da" className="flex items-center space-x-2 bg-border p-2 rounded-md hover:bg-muted transition">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <circle cx="11" cy="11" r="8" strokeWidth="2" />
                <path d="m21 21-4.3-4.3" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <span className="truncate">Tata Consultancy previous employees</span>
            </Link>
            {/* Add more recent searches as needed */}
          </div>
          <Link to="/history" className="flex items-center justify-between px-2 py-1 mt-2 text-sm font-medium text-muted-foreground hover:text-foreground transition">
            <span>View all</span>
            {/* Chevron Icon */}
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 15 15" stroke="currentColor">
              <path d="M8.146 3.146a.5.5 0 011 0l4 4a.5.5 0 010 .708l-4 4a.5.5 0 01-.708-.708L11.793 8.5 7.438 4.146a.5.5 0 010-.708z" />
            </svg>
          </Link>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;

