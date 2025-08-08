# Overview

SyncTunes is a web application that enables users to synchronize playlists between Spotify and YouTube Music platforms. The application provides secure user authentication, platform account linking through OAuth, playlist management, and bidirectional sync capabilities between the two music streaming services. The system tracks sync history and provides users with detailed logging of their synchronization activities.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture
- **Framework**: Flask-based Python web application with modular route organization
- **Database**: Custom in-memory database implementation with thread-safe operations and auto-incrementing primary keys
- **Authentication**: Session-based user authentication with secure password hashing using Werkzeug
- **API Integration**: Modular service layer for Spotify Web API and YouTube Music API integration

## Database Design
- **Storage Strategy**: In-memory database with SQL-like schema structure for development/testing
- **Schema**: Normalized relational design with separate tables for users, platforms, user accounts, playlists, songs, and sync logs
- **Thread Safety**: Thread-safe operations using RLock for concurrent access protection
- **Data Model**: Support for multiple platform accounts per user with OAuth token storage

## Frontend Architecture
- **Technology**: Server-side rendered HTML templates with Jinja2 templating
- **Styling**: Minimal black and white CSS design with responsive grid layouts
- **JavaScript**: Vanilla JavaScript for API interactions using fetch API
- **User Interface**: Clean, functional interface focused on core playlist sync functionality

## Authentication & Authorization
- **User Authentication**: Session-based authentication with secure password hashing
- **OAuth Integration**: Spotify OAuth 2.0 flow for secure platform account linking
- **Session Management**: Flask session handling with configurable secret keys
- **Platform Tokens**: Secure storage of OAuth access tokens for API authentication

## API Integration Strategy
- **Spotify Integration**: Full OAuth 2.0 implementation with playlist read/write permissions
- **YouTube Music Integration**: Public API access through ytmusicapi for song search and matching
- **Error Handling**: Comprehensive error handling and logging for API failures
- **Rate Limiting**: Consideration for API rate limits in sync operations

# External Dependencies

## Music Platform APIs
- **Spotify Web API**: OAuth 2.0 authentication, playlist management, track metadata retrieval
- **YouTube Music API (ytmusicapi)**: Song search, public playlist access, track matching

## Python Libraries
- **Flask**: Web framework for routing, templating, and session management
- **Werkzeug**: Security utilities for password hashing and request handling
- **Requests**: HTTP client library for external API communications
- **python-dotenv**: Environment variable management for configuration

## Development Tools
- **Environment Configuration**: dotenv for managing API credentials and configuration
- **Logging**: Python logging module for debugging and error tracking
- **Threading**: Python threading module for database thread safety

## Frontend Assets
- **CSS Framework**: Custom responsive CSS with system font stack
- **Icons/Fonts**: System fonts (-apple-system, BlinkMacSystemFont, Segoe UI)
- **No External CDNs**: Self-contained frontend with no external dependencies