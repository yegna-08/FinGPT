"use client"
import { useState } from 'react';

const InferenceComponent = () => {
    const [model, setModel] = useState('finma_deepspeed'); // default to finma
    const [inputText, setInputText] = useState('');
    const [response, setResponse] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleModelChange = (event) => {
        setModel(event.target.value);
    };

    const handleInputChange = (event) => {
        setInputText(event.target.value);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        setIsLoading(true);
        setResponse('');
    
        try {
            const response = await fetch(`http://192.168.10.131:5000/${model}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: inputText }),
            });
    
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
    
            const data = await response.json();
            setResponse(data.response);
        } catch (error) {
            console.error('Error:', error);
            setResponse('Failed to generate response.');
        } finally {
            setIsLoading(false);
        }
    };
    

    return (
        <div>
            <form 
            className="flex flex-col items-center justify-center gap-4 mt-20 bordered"
            onSubmit={handleSubmit}>
                <label>
                    Choose a Model:
                    <select value={model} onChange={handleModelChange} className="select select-accent w-full max-w-xs text-black">
                        <option value="finma">Finma</option>
                        <option value="fingpt">FinGPT</option>
                        <option value="finma_deepspeed">Finma(DeepSpeed)</option>
                    </select>
                </label>
                <br />
                <label>
                Input Text:
                <input type="text" placeholder="Type here" className="input input-bordered w-full max-w-xs" value={inputText} onChange={handleInputChange}/>
                    
                </label>
                <br />
                <button className= "btn btn-accent" type="submit" disabled={isLoading}>
                    Generate
                </button>
            </form>
            <div>
                <h3>Response:</h3>
                <p>{isLoading ? 'Generating...' : response}</p>
            </div>
        </div>
    );
};

export default InferenceComponent;
