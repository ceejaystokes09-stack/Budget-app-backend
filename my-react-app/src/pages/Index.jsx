import { useEffect, useState } from "react";
import "../index.css";
import Header from "../components/Header.jsx";
import Footer from "../components/Footer.jsx";
import NewTaskForm from "../components/New-Task.jsx";
import Group from "../components/Group.jsx";
import { useFetcher } from "react-router-dom";

function readSavedItems(key) {
  try {
    const saved = JSON.parse(localStorage.getItem(key) || "[]");
    return Array.isArray(saved) ? saved : [];
  } catch {
    return [];
  }
}

function createId() {
  return (
    globalThis.crypto?.randomUUID?.() ||
    `${Date.now()}-${Math.random().toString(36).slice(2)}`
  );
}

async function getData() {
  const response = await fetch("api/details/user-details");
  const data = await response.json();

  if (response.ok) {
    return data;
  } else return {};
}

export default function App() {
  const [groups, setGroups] = useState(() => readSavedItems("groups"));
  const [tasks, setTasks] = useState(() => readSavedItems("tasks"));
  const [groupName, setGroupName] = useState("");
  const [parentId, setParentId] = useState("");
  const [taskGroupId, setTaskGroupId] = useState("");
  const [taskFormOpen, setTaskFormOpen] = useState(false);
  const [isDark, setIsDark] = useState(
    () => localStorage.getItem("theme") === "dark",
  );
  const [userdata, setUserdata] = useState(() => getData());

  useEffect(() => {
    document.documentElement.dataset.theme = isDark ? "dark" : "light";
    localStorage.setItem("theme", isDark ? "dark" : "light");
  }, [isDark]);

  useEffect(() => {
    const refreshTasks = () => setTasks(readSavedItems("tasks"));
    window.addEventListener("tasksUpdated", refreshTasks);
    return () => window.removeEventListener("tasksUpdated", refreshTasks);
  }, []);

  function addGroup(event) {
    event.preventDefault();
    const name = groupName.trim();
    if (!name) return;
    //testing
    const newGroup = { id: createId(), name, parentId: parentId || null };
    const updatedGroups = [...groups, newGroup];
    localStorage.setItem("groups", JSON.stringify(updatedGroups));
    setGroups(updatedGroups);
    setGroupName("");
  }

  function openTaskForm(groupId = "") {
    setTaskGroupId(groupId);
    setTaskFormOpen(true);
  }

  function saveTask(task) {
    const updatedTasks = [...tasks, task];
    localStorage.setItem("tasks", JSON.stringify(updatedTasks));
    setTasks(updatedTasks);
    setTaskFormOpen(false);
  }

  const rootGroups = groups.filter(
    (group) =>
      !group.parentId || !groups.some((item) => item.id === group.parentId),
  );

  return (
    <>
      <Header
        isDark={isDark}
        onToggleTheme={() => setIsDark(!isDark)}
        user_data={userdata}
      />
      <main className="workspace">
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
      </main>
      <Footer onAddTask={() => openTaskForm()} canAddTask={groups.length > 0} />
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
