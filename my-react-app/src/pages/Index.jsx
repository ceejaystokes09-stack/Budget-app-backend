import { useEffect, useState } from "react";
import "../index.css";
import Header from "../components/Header.jsx";
import Footer from "../components/Footer.jsx";
import NewTaskForm from "../components/New-Task.jsx";
import Group from "../components/Group.jsx";
import { apiRequest } from "../api.js";

function readLegacyData() {
  const rawGroups = localStorage.getItem("groups");
  const rawTasks = localStorage.getItem("tasks");
  const theme = localStorage.getItem("theme");
  if (rawGroups === null && rawTasks === null && theme === null) return null;

  const groups = rawGroups === null ? [] : JSON.parse(rawGroups);
  const tasks = rawTasks === null ? [] : JSON.parse(rawTasks);
  if (!Array.isArray(groups) || !Array.isArray(tasks)) {
    throw new Error("Saved browser data is invalid and could not be imported.");
  }
  return { groups, tasks, theme };
}

function clearLegacyData() {
  localStorage.removeItem("groups");
  localStorage.removeItem("tasks");
  localStorage.removeItem("theme");
}

function createId() {
  return (
    globalThis.crypto?.randomUUID?.() ||
    `${Date.now()}-${Math.random().toString(36).slice(2)}`
  );
}

export default function App() {
  const [groups, setGroups] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [groupName, setGroupName] = useState("");
  const [parentId, setParentId] = useState("");
  const [taskGroupId, setTaskGroupId] = useState("");
  const [taskFormOpen, setTaskFormOpen] = useState(false);
  const [isDark, setIsDark] = useState(false);
  const [userdata, setUserdata] = useState({ name: "guest", email: "..." });
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadWorkspace() {
      try {
        const legacyData = readLegacyData();
        if (legacyData) {
          await apiRequest("/api/data/import-local", {
            method: "POST",
            body: JSON.stringify(legacyData),
          });
          clearLegacyData();
        }
      } catch (loadError) {
        console.error("Could not import saved browser data.", loadError);
        setError(loadError.message || "Could not import saved browser data.");
      }

      try {
        const [workspace, user] = await Promise.all([
          apiRequest("/api/data"),
          apiRequest("/api/details/user-details"),
        ]);
        setGroups(workspace.groups);
        setTasks(workspace.tasks);
        setIsDark(workspace.theme === "dark");
        setUserdata(user);
      } catch (loadError) {
        console.error("Could not load workspace data.", loadError);
        setError(loadError.message || "Could not load workspace data.");
      } finally {
        setIsLoading(false);
      }
    }

    loadWorkspace();
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = isDark ? "dark" : "light";
  }, [isDark]);

  async function addGroup(event) {
    event.preventDefault();
    const name = groupName.trim();
    if (!name) return;

    const newGroup = { id: createId(), name, parentId: parentId || null };
    try {
      await apiRequest("/api/data/groups", {
        method: "POST",
        body: JSON.stringify(newGroup),
      });
      setGroups((currentGroups) => [...currentGroups, newGroup]);
      setGroupName("");
      setError("");
    } catch (saveError) {
      console.error("Could not save group.", saveError);
      setError(saveError.message || "Could not save group.");
    }
  }

  async function toggleTheme() {
    const theme = isDark ? "light" : "dark";
    try {
      await apiRequest("/api/data/settings", {
        method: "PUT",
        body: JSON.stringify({ theme }),
      });
      setIsDark(theme === "dark");
      setError("");
    } catch (saveError) {
      console.error("Could not save theme preference.", saveError);
      setError(saveError.message || "Could not save theme preference.");
    }
  }

  function openTaskForm(groupId = "") {
    setTaskGroupId(groupId);
    setTaskFormOpen(true);
  }

  async function saveTask(task) {
    try {
      await apiRequest("/api/data/tasks", {
        method: "POST",
        body: JSON.stringify(task),
      });
      setTasks((currentTasks) => [...currentTasks, task]);
      setTaskFormOpen(false);
      setError("");
    } catch (saveError) {
      console.error("Could not save task.", saveError);
      setError(saveError.message || "Could not save task.");
      throw saveError;
    }
  }

  async function updateTask(task) {
    try {
      await apiRequest(`/api/data/tasks/${encodeURIComponent(task.id)}`, {
        method: "PUT",
        body: JSON.stringify(task),
      });
      setTasks((currentTasks) =>
        currentTasks.map((savedTask) =>
          savedTask.id === task.id ? task : savedTask,
        ),
      );
      setError("");
    } catch (saveError) {
      console.error("Could not update task.", saveError);
      setError(saveError.message || "Could not update task.");
      throw saveError;
    }
  }

  const rootGroups = groups.filter(
    (group) =>
      !group.parentId || !groups.some((item) => item.id === group.parentId),
  );

  return (
    <>
      <Header
        isDark={isDark}
        onToggleTheme={toggleTheme}
        user_data={userdata}
      />
      <main className="workspace">
        {error && (
          <div className="error-conc" role="alert">
            <p>{error}</p>
          </div>
        )}
        {isLoading ? (
          <p role="status">Loading your budget...</p>
        ) : (
          <>
            <section className="workspace-intro">
              <div>
                <p className="eyebrow">YOUR BUDGET, ORGANIZED</p>
                <h1>Your Finance Sorted</h1>
                <p className="workspace-subtitle">
                  Build a home for every plan, project, and purchase.
                </p>
              </div>
              <span className="group-count">
                {groups.length} {groups.length === 1 ? "group" : "groups"}
              </span>
            </section>

            <form className="group-create" onSubmit={addGroup}>
              <label className="group-name-field">
                <span>New group</span>
                <input
                  value={groupName}
                  onChange={(event) => setGroupName(event.target.value)}
                  placeholder="e.g. Home renovation"
                />
              </label>
              <label className="group-parent-field">
                <span>Location</span>
                <select
                  value={parentId}
                  onChange={(event) => setParentId(event.target.value)}
                >
                  <option value="">Top level</option>
                  {groups.map((group) => (
                    <option key={group.id} value={group.id}>
                      {group.name}
                    </option>
                  ))}
                </select>
              </label>
              <button className="create-group-button" type="submit">
                <span aria-hidden="true">+</span> Create group
              </button>
            </form>

            {rootGroups.length ? (
              <section className="group-tree" aria-label="Your groups">
                {rootGroups.map((group) => (
                  <Group
                    key={group.id}
                    group={group}
                    groups={groups}
                    tasks={tasks}
                    onAddTask={openTaskForm}
                    onUpdateTask={updateTask}
                  />
                ))}
              </section>
            ) : (
              <section className="empty-groups">
                <span className="empty-groups-mark" aria-hidden="true">
                  +
                </span>
                <h2>Your spaces start here</h2>
                <p>
                  Create a group above. Choose “Top level” to start a space, or
                  place it inside another group.
                </p>
              </section>
            )}
          </>
        )}
      </main>
      <Footer
        onAddTask={() => openTaskForm()}
        canAddTask={groups.length > 0}
      />
      <NewTaskForm
        groups={groups}
        selectedGroupId={taskGroupId}
        onSelectGroup={setTaskGroupId}
        isOpen={taskFormOpen}
        onClose={() => setTaskFormOpen(false)}
        onSave={saveTask}
      />
    </>
  );
}
