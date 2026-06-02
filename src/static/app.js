document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  function showMessage(text, type = "info") {
    messageDiv.textContent = text;
    messageDiv.className = type;
    messageDiv.classList.remove("hidden");

    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  async function fetchActivities() {
    try {
      const response = await fetch("/activities", { cache: "no-store" });
      const activities = await response.json();

      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";
        activityCard.dataset.activityName = name;

        const title = document.createElement("h4");
        title.textContent = name;

        const description = document.createElement("p");
        description.textContent = details.description;

        const schedule = document.createElement("p");
        schedule.innerHTML = `<strong>Schedule:</strong> ${details.schedule}`;

        const availability = document.createElement("p");
        availability.innerHTML = `<strong>Availability:</strong> ${details.max_participants - details.participants.length} spots left`;

        activityCard.append(title, description, schedule, availability);

        if (details.participants.length) {
          const participantsSection = document.createElement("div");
          participantsSection.className = "participants-section";

          const participantsLabel = document.createElement("p");
          participantsLabel.innerHTML = "<strong>Participants:</strong>";

          const participantsList = document.createElement("ul");
          participantsList.className = "participants-list";

          details.participants.forEach((participant) => {
            const listItem = document.createElement("li");
            listItem.className = "participant-item";

            const nameText = document.createElement("span");
            nameText.textContent = participant;

            const deleteButton = document.createElement("button");
            deleteButton.type = "button";
            deleteButton.className = "participant-delete-btn";
            deleteButton.dataset.activity = name;
            deleteButton.dataset.email = participant;
            deleteButton.setAttribute("aria-label", `Remove ${participant} from ${name}`);
            deleteButton.textContent = "×";

            listItem.append(nameText, deleteButton);
            participantsList.appendChild(listItem);
          });

          participantsSection.append(participantsLabel, participantsList);
          activityCard.appendChild(participantsSection);
        } else {
          const noParticipants = document.createElement("p");
          noParticipants.className = "no-participants";
          noParticipants.innerHTML = "<strong>Participants:</strong> None yet";
          activityCard.appendChild(noParticipants);
        }

        activitiesList.appendChild(activityCard);

        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  async function removeParticipant(activityName, email) {
    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activityName)}/participants?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        fetchActivities();
      } else {
        showMessage(result.detail || "Could not remove participant", "error");
      }
    } catch (error) {
      showMessage("Failed to remove participant. Please try again.", "error");
      console.error("Error removing participant:", error);
    }
  }

  activitiesList.addEventListener("click", (event) => {
    const deleteButton = event.target.closest(".participant-delete-btn");
    if (!deleteButton) {
      return;
    }

    const activityName = deleteButton.dataset.activity;
    const email = deleteButton.dataset.email;
    if (!activityName || !email) {
      return;
    }

    removeParticipant(activityName, email);
  });

  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        signupForm.reset();
        await fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  fetchActivities();
});
