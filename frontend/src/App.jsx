import { useEffect, useState } from "react";

function App() {
  const [message, setMessage] = useState("Connecting to GreenMind AI...");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/")
      .then((response) => response.json())
      .then((data) => {
        setMessage(data.message);
      })
      .catch(() => {
        setMessage("Could not connect to GreenMind AI backend.");
      });
  }, []);

  return (
    <div>
      <h1>GreenMind AI</h1>
      <p>{message}</p>
    </div>
  );
}

export default App;