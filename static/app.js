document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("queryForm");
    const input = document.getElementById("questionInput");
    const chatContainer = document.getElementById("chatContainer");
    const clearBtn = document.getElementById("clearBtn");
    
    // Add a message to the chat
    function addMessage(content, type) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `message ${type}-message`;
        
        if (typeof content === "string") {
            msgDiv.textContent = content;
        } else {
            msgDiv.appendChild(content);
        }
        
        chatContainer.appendChild(msgDiv);
        scrollToBottom();
        return msgDiv;
    }
    
    // Show a loading indicator
    function showTyping() {
        const typingDiv = document.createElement("div");
        typingDiv.className = "message ai-message typing";
        typingDiv.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
        typingDiv.id = "typingIndicator";
        chatContainer.appendChild(typingDiv);
        scrollToBottom();
    }
    
    // Remove loading indicator
    function removeTyping() {
        const typing = document.getElementById("typingIndicator");
        if (typing) typing.remove();
    }
    
    // Scroll chat to bottom
    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Build the AI response HTML (SQL + Table + Errors)
    function buildAIResponse(data) {
        const container = document.createElement("div");
        
        if (data.sql) {
            const sqlTitle = document.createElement("div");
            sqlTitle.textContent = "Generated SQL:";
            sqlTitle.style.fontSize = "0.8rem";
            sqlTitle.style.color = "var(--text-secondary)";
            container.appendChild(sqlTitle);
            
            const sqlBox = document.createElement("div");
            sqlBox.className = "sql-box";
            sqlBox.textContent = data.sql;
            container.appendChild(sqlBox);
        }
        
        if (data.success && data.result && data.result.columns) {
            if (data.result.rows.length === 0) {
                const empty = document.createElement("div");
                empty.textContent = "Query executed successfully, but returned 0 rows.";
                empty.style.color = "var(--text-secondary)";
                container.appendChild(empty);
            } else {
                const wrapper = document.createElement("div");
                wrapper.className = "table-wrapper";
                
                const table = document.createElement("table");
                
                // Header
                const thead = document.createElement("thead");
                const trHead = document.createElement("tr");
                data.result.columns.forEach(col => {
                    const th = document.createElement("th");
                    th.textContent = col;
                    trHead.appendChild(th);
                });
                thead.appendChild(trHead);
                table.appendChild(thead);
                
                // Body
                const tbody = document.createElement("tbody");
                data.result.rows.forEach(row => {
                    const tr = document.createElement("tr");
                    data.result.columns.forEach(col => {
                        const td = document.createElement("td");
                        td.textContent = row[col] !== null ? row[col] : "NULL";
                        tr.appendChild(td);
                    });
                    tbody.appendChild(tr);
                });
                table.appendChild(tbody);
                wrapper.appendChild(table);
                container.appendChild(wrapper);
                
                if (data.result.truncated) {
                    const trunc = document.createElement("div");
                    trunc.textContent = `Showing top ${data.result.row_count} rows (results truncated).`;
                    trunc.style.fontSize = "0.75rem";
                    trunc.style.color = "var(--text-secondary)";
                    trunc.style.marginTop = "8px";
                    container.appendChild(trunc);
                }
            }
        } else if (!data.success && data.error) {
            const errDiv = document.createElement("div");
            errDiv.className = "error-text";
            errDiv.textContent = `Error: ${data.error}`;
            container.appendChild(errDiv);
        } else {
            const errDiv = document.createElement("div");
            errDiv.className = "error-text";
            errDiv.textContent = "An unknown error occurred.";
            container.appendChild(errDiv);
        }
        
        return container;
    }

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const question = input.value.trim();
        if (!question) return;
        
        // Add user message
        addMessage(question, "user");
        input.value = "";
        
        // Show typing
        showTyping();
        
        try {
            const response = await fetch("/api/query", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question })
            });
            
            const data = await response.json();
            removeTyping();
            addMessage(buildAIResponse(data), "ai");
            
        } catch (error) {
            removeTyping();
            addMessage("Failed to connect to the server.", "ai");
        }
    });
    
    clearBtn.addEventListener("click", async () => {
        try {
            await fetch("/api/clear", { method: "POST" });
            chatContainer.innerHTML = '<div class="message system-message">Context cleared. How can I help you next?</div>';
        } catch (e) {
            console.error("Failed to clear context");
        }
    });
});
