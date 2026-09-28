import "../index.css"
import Toggle from "./Slider"

function createId() {
    return globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(36).slice(2)}`
}

function NewTaskForm({ groups, selectedGroupId, onSelectGroup, isOpen, onClose, onSave }) {
    function save(event) {
        event.preventDefault()
        const form = event.currentTarget
        const name = form.elements.taskName.value.trim()
        const description = form.elements.description.value.trim()
        const groupId = form.elements.groupId.value

        if (!name || !description || !groupId) return

        onSave({
            id: createId(),
            groupId,
            name: name.charAt(0).toUpperCase() + name.slice(1),
            description: description.charAt(0).toUpperCase() + description.slice(1),
            maxPrice: Number(form.elements.maxPrice.value) || 0,
            currentPrice: Number(form.elements.currentPrice.value) || 0,
            isGroup: form.elements.toggle.checked,
        })
        form.reset()
    }

    return (
        <div className={`full-screen blur center new-task ${isOpen ? "is-visible" : ""}`} aria-hidden={!isOpen}>
            <form className="input-feild" onSubmit={save}>
                <div className="task-form-heading">
                    <div>
                        <p className="eyebrow">ADD TO YOUR PLAN</p>
                        <h1>New task</h1>
                    </div>
                    <button type="button" className="task-form-close" onClick={onClose} aria-label="Close">×</button>
                </div>
                <label className="task-form-field">
                    <span>Task name</span>
                    <input type="text" name="taskName" placeholder="Enter task name" required />
                </label>
                <label className="task-form-field">
                    <span>Description</span>
                    <textarea name="description" placeholder="What are you planning?" rows="3" required />
                </label>
                <label className="task-form-field">
                    <span>Group</span>
                    <select name="groupId" value={selectedGroupId} onChange={(event) => onSelectGroup(event.target.value)} required>
                        <option value="" disabled>Choose a group</option>
                        {groups.map((group) => (
                            <option key={group.id} value={group.id}>
                                {group.parentId ? "↳ " : ""}{group.name}
                            </option>
                        ))}
                    </select>
                </label>
                <div className="task-form-amounts">
                    <label className="task-form-field">
                        <span>Budget</span>
                        <input type="number" name="maxPrice" min="0" placeholder="0" />
                    </label>
                    <label className="task-form-field">
                        <span>Spent</span>
                        <input type="number" name="currentPrice" min="0" placeholder="0" />
                    </label>
                </div>
                <label className="task-complete-toggle">
                    <Toggle />
                    <span>Mark as complete</span>
                </label>
                <button className="task-form-submit" type="submit">Save task</button>
            </form>
        </div>
    )
}

export default NewTaskForm
