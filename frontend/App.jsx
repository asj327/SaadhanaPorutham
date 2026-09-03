import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [objectType, setObjectType] = useState("");
  const [profile, setProfile] = useState(null);
  const [objectId, setObjectId] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [actionMessage, setActionMessage] = useState("");

  // Generate an AI profile
  const generateProfile = async () => {
    if (!objectType.trim()) {
      setError("Please enter an object.");
      return;
    }

    setLoading(true);
    setError("");
    setProfile(null);
    setObjectId(null);
    setActionMessage("");

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/objects/generate",
        null,
        {
          params: {
            object_type: objectType,
          },
        }
      );

      if (response.data.status !== "success") {
        throw new Error(response.data.message);
      }

      const generatedProfile = JSON.parse(response.data.profile);

      setProfile(generatedProfile);
      setObjectId(response.data.object_id);
    } catch (err) {
      console.error("Generate error:", err);
      setError("Could not generate profile. Check your backend.");
    } finally {
      setLoading(false);
    }
  };

  // Like object
  const handleLike = async () => {
    if (!objectId) return;

    try {
      await axios.post(
        `http://127.0.0.1:8000/objects/${objectId}/like`
      );

      setActionMessage("You liked this object!");
    } catch (err) {
      console.error("Like error:", err);
      setActionMessage("Could not save your like.");
    }
  };

  // Pass object
  const handlePass = async () => {
    if (!objectId) return;

    try {
      await axios.post(
        `http://127.0.0.1:8000/objects/${objectId}/pass`
      );

      setActionMessage("Maybe next time...");
    } catch (err) {
      console.error("Pass error:", err);
      setActionMessage("Could not save your choice.");
    }
  };

  return (
    <div className="app">

      <header>
        <h1>
          saadhanaPorutham
        </h1>

        <p>
          Where everyday objects find their perfect match.
        </p>
      </header>

      {/* Object Generator */}

      <div className="generator">

        <input
          type="text"
          placeholder="Enter an object..."
          value={objectType}
          onChange={(e) => setObjectType(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              generateProfile();
            }
          }}
        />

        <button
          onClick={generateProfile}
          disabled={loading}
        >
          {loading
            ? "Creating profile..."
            : "Create Profile"}
        </button>

      </div>

      {/* Error */}

      {error && (
        <p className="error">
          {error}
        </p>
      )}

      {/* Loading */}

      {loading && (
        <div className="loading">
          Creating your object's dating profile...
        </div>
      )}

      {/* Profile */}

      {profile && !loading && (
        <div className="profile">

          <h2>{profile.name}</h2>

          <p className="object-type">
            {profile.type}
          </p>

          <div className="profile-section">
            <h3>Bio</h3>
            <p>{profile.bio}</p>
          </div>

          <div className="profile-section">
            <h3>Personality</h3>
            <p>{profile.personality}</p>
          </div>

          <div className="profile-section">
            <h3>Attachment Style</h3>
            <p>{profile.attachment_style}</p>
          </div>

          <div className="profile-section">
            <h3>Love Language</h3>
            <p>{profile.love_language}</p>
          </div>

          <div className="profile-section">
            <h3>Turn Ons</h3>
            <p>{profile.turn_ons}</p>
          </div>

          <div className="profile-section">
            <h3>Turn Offs</h3>
            <p>{profile.turn_offs}</p>
          </div>

          <div className="profile-section green">
            <h3>Green Flags</h3>
            <p>{profile.green_flags}</p>
          </div>

          <div className="profile-section red">
            <h3>Red Flags</h3>
            <p>{profile.red_flags}</p>
          </div>

          {/* Like / Pass */}

          <div className="actions">

            <button
              className="pass-btn"
              onClick={handlePass}
            >
              {"\u2715"} Pass
            </button>

            <button
              className="like-btn"
              onClick={handleLike}
            >
              {"\u2764\uFE0F"} Like
            </button>

          </div>

          {/* Action message */}

          {actionMessage && (
            <p className="action-message">
              {actionMessage}
            </p>
          )}

        </div>
      )}

    </div>
  );
}

export default App;
