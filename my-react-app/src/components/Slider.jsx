import { useState } from "react";
import "../index.css"

function Toggle(){
    const [isChecked, setIsChecked] = useState(false);

    return (
        <>
            <div style={{width: "max-content"}} className="Toggle-Focus">
                <input type="checkbox" id="toggle" className="toggle-checkbox" checked={isChecked} onChange={(event) => setIsChecked(event.target.checked)} />
                <label htmlFor="toggle" className="toggle-label">
                    <span className="toggle-inner-button"></span>
                </label>
            </div>
        </>
    )
}

export default Toggle