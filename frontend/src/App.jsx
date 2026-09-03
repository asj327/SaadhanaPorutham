import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [objectType, setObjectType] = useState("");
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [decision, setDecision] = useState("");

  const generateProfile = async () => {
    if (!objectType.trim()) {
      setError("Please enter an object.");
      return;
    }

    setLoading(true);
    setError("");
    setProfile(null);
    setDecision("");

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

      const generatedProfile = JSON.parse(response.data.profile);
      setProfile(generatedProfile);
    } catch (err) {
      console.error(err);
      setError("Could not generate profile. Check your backend.");
    } finally {
      setLoading(false);
    }
  };

  const handleLike = () => {
    setDecision("liked");
  };

  const handlePass = () => {
    setDecision("passed");
  };

  return (
    <div className="app">
      <h1>saadhanaPorutham ??</h1>

      <p>Where everyday objects find their perfect match.</p>

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

        <button onClick={generateProfile} disabled={loading}>
          {loading ? "Creating profile..." : "Create Profile ?"}
        </button>
      </div>

      {error && <p className="error">{error}</p>}

      {profile && (
        <div className="profile">
          <div className="profile-header">
            <span className="badge">AI GENERATED</span>
          </div>

          <h2>{profile.name}</h2>

          <p className="bio">"{profile.bio}"</p>

          <div className="profile-details">
            <p><strong>Type:</strong> {profile.type}</p>
            <p><strong>Personality:</strong> {profile.personality}</p>
            <p><strong>Attachment Style:</strong> {profile.attachment_style}</p>
            <p><strong>Love Language:</strong> {profile.love_language}</p>
            <p><strong>Turn Ons:</strong> {profile.turn_ons}</p>
            <p><strong>Turn Offs:</strong> {profile.turn_offs}</p>
            <p><strong>?? Green Flags:</strong> {profile.green_flags}</p>
            <p><strong>?? Red Flags:</strong> {profile.red_flags}</p>
          </div>

          <div className="actions">
            <button className="pass-btn" onClick={handlePass}>
              ?
            </button>

            <button className="like-btn" onClick={handleLike}>
              ??
            </button>
          </div>

          {decision === "liked" && (
            <div className="decision liked">
              ?? You liked this object!
            </div>
          )}

          {decision === "passed" && (
            <div className="decision passed">
              ? Maybe next time...
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;

