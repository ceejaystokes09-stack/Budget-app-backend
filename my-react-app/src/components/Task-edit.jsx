import "../index.css"
import { useEffect, useState } from "react"

function Edit({ task, onClose, onSave }) {
    const [isVisible, setIsVisible] = useState(false)
    const [error, setError] = useState("")

    useEffect(() => {
        const frame = requestAnimationFrame(() => setIsVisible(true))
        return () => cancelAnimationFrame(frame)
    }, [])

    if (!task) return null

    function handleClose() {
        setIsVisible(false)
        window.setTimeout(onClose, 200)
    }

    async function Save(){
        const updatedTask = {
            ...task,
            name: document.querySelector(".Task-edit #new-name").value.trim(),
            description: document.querySelector(".Task-edit #new-desc").value.trim(),
            maxPrice: Number(document.querySelector(".Task-edit #new-max").value) || 0,
            currentPrice: Number(document.querySelector(".Task-edit #new-Current").value) || 0,
        }

        try {
            await onSave(updatedTask)
            setError("")
            handleClose()
        } catch (saveError) {
            setError(saveError.message || "Could not update task.")
        }
    }

    return (
        <div className={`Task-edit ${isVisible ? "is-visible" : ""}`}>
            <div className="Task-edit__panel">
                <div className="Task-edit__header">
                    <h3>Edit Task</h3>
                    <button type="button" className="Task-edit__save" onClick={Save} >Save</button>
                    <button type="button" className="Task-edit__close" onClick={handleClose}>✕</button>
                    
                </div>
                {error && <p role="alert">{error}</p>}

                <label>
                    Name
                    <input defaultValue={task.name} id="new-name" />
                </label>

                <label>
                    Description
                    <textarea defaultValue={task.description} rows="4" id="new-desc" />
                </label>

                <div className="Task-edit__row">
                    <label>
                        Max
                        <input type="number" defaultValue={task.maxPrice} id="new-max" />
                    </label>

                    <label>
                        Current
                        <input type="number" defaultValue={task.currentPrice} id="new-Current" />
                    </label>
                </div>

                <button type="button" className="Task-edit__complete">Mark As Complete</button>
            </div>
        </div>
    )
}

export default Edit