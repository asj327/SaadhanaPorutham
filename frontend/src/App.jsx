import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

// Railway backend
const API = "https://unique-curiosity-production-3298.up.railway.app";

function App() {
  const [objectType, setObjectType] = useState("");

  const [profile, setProfile] = useState(null);
  const [objectId, setObjectId] = useState(null);

  const [objects, setObjects] = useState([]);
  const [selected, setSelected] = useState([]);

  const [loading, setLoading] = useState(false);
  const [loadingObjects, setLoadingObjects] = useState(false);

  const [error, setError] = useState("");
  const [actionMessage, setActionMessage] = useState("");

  const [compatibility, setCompatibility] = useState(null);
  const [compatibilityLoading, setCompatibilityLoading] = useState(false);

  // --------------------------------
  // Load all objects from Firestore
  // --------------------------------

  const loadObjects = async () => {
    setLoadingObjects(true);
    setError("");

    try {
      const response = await axios.get(`${API}/objects`);

      if (response.data.status === "success") {
        setObjects(response.data.objects);
      } else {
        setError("Could not load objects.");
      }
    } catch (err) {
      console.error("Load objects error:", err);
      setError("Could not connect to the backend.");
    } finally {
      setLoadingObjects(false);
    }
  };

  // Load objects when page opens
  useEffect(() => {
    loadObjects();
  }, []);

  // --------------------------------
  // Generate AI profile
  // --------------------------------

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
        `${API}/objects/generate`,
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

      const generatedProfile =
        typeof response.data.profile === "string"
          ? JSON.parse(response.data.profile)
          : response.data.profile;

      setProfile(generatedProfile);
      setObjectId(response.data.object_id);

      // Refresh Discover section
      await loadObjects();

      setObjectType("");
    } catch (err) {
      console.error("Generate error:", err);

      setError(
        err.response?.data?.detail ||
          "Could not generate profile. Check your backend."
      );
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------
  // Like
  // --------------------------------

  const handleLike = async (id) => {
    if (!id) return;

    try {
      await axios.post(`${API}/objects/${id}/like`);

      setActionMessage("You liked this object.");
    } catch (err) {
      console.error("Like error:", err);
      setActionMessage("Could not save your like.");
    }
  };

  // --------------------------------
  // Pass
  // --------------------------------

  const handlePass = async (id) => {
    if (!id) return;

    try {
      await axios.post(`${API}/objects/${id}/pass`);

      setActionMessage("Maybe next time.");
    } catch (err) {
      console.error("Pass error:", err);
      setActionMessage("Could not save your choice.");
    }
  };

  // --------------------------------
  // Select / deselect profile
  // --------------------------------

  const toggleSelection = (object) => {
    const alreadySelected = selected.some(
      (item) => item.id === object.id
    );

    // Deselect
    if (alreadySelected) {
      setSelected(
        selected.filter(
          (item) => item.id !== object.id
        )
      );

      return;
    }

    // Maximum 2
    if (selected.length >= 2) {
      setActionMessage(
        "You can select only two objects."
      );

      return;
    }

    setSelected([...selected, object]);
    setActionMessage("");
  };

  // --------------------------------
  // Compatibility
  // --------------------------------

  const checkCompatibility = async () => {
    if (selected.length !== 2) {
      setActionMessage(
        "Please select exactly two objects."
      );

      return;
    }

    setCompatibilityLoading(true);
    setCompatibility(null);
    setActionMessage("");

    try {
      const response = await axios.post(
        `${API}/objects/compatibility`,
        null,
        {
          params: {
            object1_id: selected[0].id,
            object2_id: selected[1].id,
          },
        }
      );

      if (response.data.status !== "success") {
        throw new Error(response.data.message);
      }

      setCompatibility(response.data.compatibility);
    } catch (err) {
      console.error(
        "Compatibility error:",
        err
      );

      setActionMessage(
        err.response?.data?.detail ||
          "Could not calculate compatibility."
      );
    } finally {
      setCompatibilityLoading(false);
    }
  };

  return (
    <div className="app">

      {/* ============================= */}
      {/* HEADER */}
      {/* ============================= */}

      <header className="header">

        <h1>
          Saadhana Porutham
        </h1>

        <p>
          Where everyday objects find their perfect match.
        </p>

      </header>


      {/* ============================= */}
      {/* CREATE PROFILE */}
      {/* ============================= */}

      <section className="create-section">

        <h2>Create an Object Profile</h2>

        <p>
          Give us an object and AI will create its dating
          personality.
        </p>

        <div className="generator">

          <input
            type="text"
            placeholder="Enter an object..."
            value={objectType}
            onChange={(e) =>
              setObjectType(e.target.value)
            }
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

      </section>


      {/* ============================= */}
      {/* ERROR */}
      {/* ============================= */}

      {error && (
        <p className="error">
          {error}
        </p>
      )}


      {/* ============================= */}
      {/* NEWLY GENERATED PROFILE */}
      {/* ============================= */}

      {profile && !loading && (

        <section className="generated-section">

          <h2>New Profile</h2>

          <div className="profile">

            <h2>{profile.name}</h2>

            <p className="object-type">
              {profile.type}
            </p>

            <div className="profile-detail">
              <strong>Bio</strong>
              <p>{profile.bio}</p>
            </div>

            <div className="profile-detail">
              <strong>Personality</strong>
              <p>{profile.personality}</p>
            </div>

            <div className="profile-detail">
              <strong>Attachment Style</strong>
              <p>{profile.attachment_style}</p>
            </div>

            <div className="profile-detail">
              <strong>Love Language</strong>
              <p>{profile.love_language}</p>
            </div>

            <div className="profile-detail">
              <strong>Turn Ons</strong>
              <p>{profile.turn_ons}</p>
            </div>

            <div className="profile-detail">
              <strong>Turn Offs</strong>
              <p>{profile.turn_offs}</p>
            </div>

            <div className="profile-detail green">
              <strong>Green Flags</strong>
              <p>{profile.green_flags}</p>
            </div>

            <div className="profile-detail red">
              <strong>Red Flags</strong>
              <p>{profile.red_flags}</p>
            </div>


            {/* Like / Pass */}

            <div className="actions">

              <button
                className="pass-btn"
                onClick={() =>
                  handlePass(objectId)
                }
              >
                {"\u2715"} Pass
              </button>

              <button
                className="like-btn"
                onClick={() =>
                  handleLike(objectId)
                }
              >
                {"\u2665"} Like
              </button>

            </div>

          </div>

        </section>

      )}


      {/* ============================= */}
      {/* DISCOVER */}
      {/* ============================= */}

      <section className="discover">

        <div className="discover-header">

          <div>

            <h2>
              Discover Objects
            </h2>

            <p>
              Browse all the objects created so far.
            </p>

          </div>

          <div className="selection-count">
            {selected.length}/2 selected
          </div>

        </div>


        {/* Loading */}

        {loadingObjects && (
          <p className="loading">
            Loading objects...
          </p>
        )}


        {/* Empty */}

        {!loadingObjects &&
          objects.length === 0 && (

            <div className="empty">

              <h3>
                No objects yet
              </h3>

              <p>
                Create the first profile above.
              </p>

            </div>

          )}


        {/* Object cards */}

        {!loadingObjects &&
          objects.length > 0 && (

            <div className="object-grid">

              {objects.map((object) => {

                const isSelected =
                  selected.some(
                    (item) =>
                      item.id === object.id
                  );

                return (

                  <div
                    key={object.id}
                    className={`object-card ${
                      isSelected
                        ? "selected-card"
                        : ""
                    }`}
                  >

                    {/* Select */}

                    <button
                      className="select-button"
                      onClick={() =>
                        toggleSelection(object)
                      }
                    >
                      {isSelected
                        ? "Selected"
                        : "Select"}
                    </button>


                    {/* Name */}

                    <h3>
                      {object.name}
                    </h3>


                    {/* Type */}

                    <p className="card-type">
                      {object.type}
                    </p>


                    {/* Bio */}

                    <p className="card-bio">
                      {object.bio}
                    </p>


                    {/* Personality */}

                    <div className="card-info">

                      <strong>
                        Personality
                      </strong>

                      <p>
                        {object.personality}
                      </p>

                    </div>


                    {/* Love language */}

                    <div className="card-info">

                      <strong>
                        Love Language
                      </strong>

                      <p>
                        {object.love_language}
                      </p>

                    </div>


                    {/* Green flags */}

                    <div className="card-info">

                      <strong>
                        Green Flags
                      </strong>

                      <p>
                        {object.green_flags}
                      </p>

                    </div>


                    {/* Actions */}

                    <div className="card-actions">

                      <button
                        className="pass-btn"
                        onClick={() =>
                          handlePass(object.id)
                        }
                      >
                        {"\u2715"} Pass
                      </button>

                      <button
                        className="like-btn"
                        onClick={() =>
                          handleLike(object.id)
                        }
                      >
                        {"\u2665"} Like
                      </button>

                    </div>

                  </div>

                );
              })}

            </div>

          )}

      </section>


      {/* ============================= */}
      {/* COMPATIBILITY */}
      {/* ============================= */}

      <section className="compatibility">

        <h2>
          Jathakam Porutham
        </h2>

        <p>
          Select exactly two objects and discover their
          fictional Jathakam match.
        </p>


        {/* Selected objects */}

        <div className="selected-profiles">

          {selected.length === 0 && (
            <p className="selection-hint">
              Select two profiles from Discover.
            </p>
          )}

          {selected.map((object) => (

            <div
              className="selected-profile"
              key={object.id}
            >

              <h3>
                {object.name}
              </h3>

              <p>
                {object.type}
              </p>

            </div>

          ))}

        </div>


        {/* Compatibility button */}

        <button
          className="compatibility-button"
          disabled={
            selected.length !== 2 ||
            compatibilityLoading
          }
          onClick={checkCompatibility}
        >
          {compatibilityLoading
            ? "Reading Jathakam..."
            : "Check Jathakam Porutham"}
        </button>


        {/* Compatibility result */}

        {compatibility && (

          <div className="compatibility-result">

            <h2>
              Jathakam Porutham
            </h2>

            <div className="jathakam-pair">

              <span>
                {compatibility.object1?.name ||
                  "Object 1"}
              </span>

              <span>+</span>

              <span>
                {compatibility.object2?.name ||
                  "Object 2"}
              </span>

            </div>


            <div className="score">
              {compatibility.total_score ?? 0}/100
            </div>

            <p className="score-label">
              Porutham Score
            </p>


            {/* 10 Poruthams */}

            <div className="porutham-grid">

              <div className="porutham-item">
                <strong>Dina Porutham</strong>
                <span>
                  {compatibility.poruthams?.dina?.score ?? 0}/10
                </span>
                <p>
                  {compatibility.poruthams?.dina?.explanation}
                </p>
              </div>

              <div className="porutham-item">
                <strong>Gana Porutham</strong>
                <span>
                  {compatibility.poruthams?.gana?.score ?? 0}/10
                </span>
                <p>
                  {compatibility.poruthams?.gana?.explanation}
                </p>
              </div>

              <div className="porutham-item">
                <strong>Mahendra Porutham</strong>
                <span>
                  {compatibility.poruthams?.mahendra?.score ?? 0}/10
                </span>
                <p>
                  {compatibility.poruthams?.mahendra?.explanation}
                </p>
              </div>

              <div className="porutham-item">
                <strong>Sthree Deergha Porutham</strong>
                <span>
                  {compatibility.poruthams?.sthree_deergha?.score ?? 0}/10
                </span>
                <p>
                  {compatibility.poruthams?.sthree_deergha?.explanation}
                </p>
              </div>

              <div className="porutham-item">
                <strong>Yoni Porutham</strong>
                <span>
                  {compatibility.poruthams?.yoni?.score ?? 0}/10
                </span>
                <p>
                  {compatibility.poruthams?.yoni?.explanation}
                </p>
              </div>

              <div className="porutham-item">
                <strong>Rashi Porutham</strong>
                <span>
                  {compatibility.poruthams?.rashi?.score ?? 0}/10
                </span>
                <p>
                  {compatibility.poruthams?.rashi?.explanation}
                </p>
              </div>

              <div className="porutham-item">
                <strong>Rasyadhipathi Porutham</strong>
                <span>
                  {compatibility.poruthams?.rasyadhipathi?.score ?? 0}/10
                </span>
                <p>
                  {compatibility.poruthams?.rasyadhipathi?.explanation}
                </p>
              </div>

              <div className="porutham-item">
                <strong>Vasya Porutham</strong>
                <span>
                  {compatibility.poruthams?.vasya?.score ?? 0}/10
                </span>
                <p>
                  {compatibility.poruthams?.vasya?.explanation}
                </p>
              </div>

              <div className="porutham-item">
                <strong>Rajju Porutham</strong>
                <span>
                  {compatibility.poruthams?.rajju?.score ?? 0}/10
                </span>
                <p>
                  {compatibility.poruthams?.rajju?.explanation}
                </p>
              </div>

              <div className="porutham-item">
                <strong>Vedha Porutham</strong>
                <span>
                  {compatibility.poruthams?.vedha?.score ?? 0}/10
                </span>
                <p>
                  {compatibility.poruthams?.vedha?.explanation}
                </p>
              </div>

            </div>


            {/* Final verdict */}

            <div className="jathakam-verdict">

              <h3>
                {compatibility.verdict}
              </h3>

              <p>
                {compatibility.marriage_prediction}
              </p>

            </div>

          </div>

        )}

      </section>


      {/* ============================= */}
      {/* ACTION MESSAGE */}
      {/* ============================= */}

      {actionMessage && (
        <p className="action-message">
          {actionMessage}
        </p>
      )}

    </div>
  );
}

export default App;