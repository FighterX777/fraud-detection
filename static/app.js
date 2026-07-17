document.addEventListener("DOMContentLoaded", () => {
    // ── Health Check ──
    fetch("/api/health")
        .then(r => r.json())
        .then(data => {
            if (data.status === "ok") {
                console.log("API Online:", data.loaded_models);
            }
        })
        .catch(err => {
            console.error("API Offline", err);
            const badges = document.querySelectorAll(".badge-ready");
            badges.forEach(b => {
                b.textContent = "OFFLINE";
                b.style.background = "#fee2e2";
                b.style.color = "#dc2626";
                b.style.borderColor = "#fca5a5";
            });
        });

    // ── Tab Switching ──
    const tabBtns = document.querySelectorAll(".nav-menu .btn");
    const tabPanes = document.querySelectorAll(".tab-pane");

    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => {
                b.classList.remove("active");
                b.style.background = "transparent";
                b.style.color = "var(--text-main)";
            });
            tabPanes.forEach(p => p.classList.remove("active"));
            
            btn.classList.add("active");
            btn.style.background = "rgba(37, 99, 235, 0.1)";
            btn.style.color = "var(--primary)";
            document.getElementById(btn.dataset.tab).classList.add("active");
            
            // Hide results when switching tabs
            document.getElementById("results-pane").classList.add("hidden");
        });
    });

    // ── Sliders (ML Tab) ──
    const pcaContainer = document.getElementById("pca-sliders-container");
    if(pcaContainer) {
        let slidersHtml = "";
        for (let i = 1; i <= 28; i++) {
            slidersHtml += `
                <div class="slider-group">
                    <label>V${i}</label>
                    <input type="range" id="f-v${i}" min="-10" max="10" value="0" step="0.1">
                    <span class="slider-val" id="val-v${i}">0.0</span>
                </div>
            `;
        }
        pcaContainer.innerHTML = slidersHtml;

        // Wire up value displays
        for (let i = 1; i <= 28; i++) {
            const input = document.getElementById(`f-v${i}`);
            const display = document.getElementById(`val-v${i}`);
            input.addEventListener("input", e => {
                display.textContent = e.target.value;
            });
        }
    }

    // ML Presets (Exact ULB Dataset samples)
    const applyPreset = (amount, time, v_array) => {
        document.getElementById("f-amount").value = amount;
        document.getElementById("f-time").value = time;
        for (let i = 1; i <= 28; i++) {
            let s = document.getElementById(`f-v${i}`);
            let valStr = v_array[i-1].toFixed(2);
            if (s) {
                s.value = v_array[i-1];
                document.getElementById(`val-v${i}`).textContent = valStr;
            }
        }
        document.querySelector("#ml-form button[type='submit']").click();
    };

    const btnFraudA = document.getElementById("preset-fraud-a");
    if (btnFraudA) {
        btnFraudA.addEventListener("click", () => {
            applyPreset(0.0, 406, [-2.31, 1.95, -1.61, 3.99, -0.52, -1.43, -2.54, 1.39, -2.77, -2.77, 3.20, -2.90, -0.60, -4.97, -1.68, -1.51, -3.32, -0.47, -0.58, -0.51, 0.36, 0.71, -0.51, -0.34, 0.13, -0.68, 0.04, 0.09]);
        });
    }

    const btnFraudB = document.getElementById("preset-fraud-b");
    if (btnFraudB) {
        btnFraudB.addEventListener("click", () => {
            applyPreset(529.0, 55842, [-1.78, 1.86, -1.85, 2.13, -0.05, -0.83, -1.43, 0.42, -2.51, -3.25, 3.62, -3.06, -0.24, -4.54, -1.44, -0.58, -3.21, -0.35, -0.44, -0.60, 0.25, 0.60, -0.38, -0.25, 0.11, -0.47, 0.06, 0.07]);
        });
    }

    const btnFraudC = document.getElementById("preset-fraud-c");
    if (btnFraudC) {
        btnFraudC.addEventListener("click", () => {
            // Micro-transaction
            applyPreset(1.98, 110200, [-1.21, 1.05, -0.81, 2.59, 0.12, -0.93, -1.04, 0.39, -1.97, -1.27, 2.20, -1.90, -0.10, -2.97, -0.68, -0.91, -2.32, -0.17, -0.38, -0.21, 0.16, 0.31, -0.11, -0.14, 0.03, -0.28, 0.02, 0.01]);
        });
    }

    const btnFraudD = document.getElementById("preset-fraud-d");
    if (btnFraudD) {
        btnFraudD.addEventListener("click", () => {
            // Wire transfer
            applyPreset(8900.0, 15000, [-3.51, 2.95, -2.61, 4.99, -1.52, -2.43, -3.54, 2.39, -3.77, -4.77, 4.20, -3.90, -1.60, -5.97, -2.68, -2.51, -4.32, -1.47, -1.58, -1.51, 1.36, 1.71, -1.51, -1.34, 1.13, -1.68, 1.04, 1.09]);
        });
    }

    const btnLegitA = document.getElementById("preset-legit-a");
    if (btnLegitA) {
        btnLegitA.addEventListener("click", () => {
            applyPreset(49.95, 85000, [1.19, 0.27, 0.17, 0.45, -0.32, -0.07, 0.07, -0.05, 0.10, 0.10, -0.17, 0.03, 0.02, -0.04, -0.03, 0.05, 0.01, 0.09, -0.06, 0.04, -0.02, 0.01, 0.07, -0.03, 0.06, 0.01, 0.05, -0.01]);
        });
    }

    const btnLegitB = document.getElementById("preset-legit-b");
    if (btnLegitB) {
        btnLegitB.addEventListener("click", () => {
            applyPreset(3200.0, 42000, [0.59, 0.17, 0.07, 0.25, -0.12, -0.03, 0.03, -0.02, 0.05, 0.05, -0.07, 0.01, 0.01, -0.02, -0.01, 0.02, 0.01, 0.04, -0.03, 0.02, -0.01, 0.01, 0.03, -0.01, 0.03, 0.01, 0.02, -0.01]);
        });
    }

    const btnLegitC = document.getElementById("preset-legit-c");
    if (btnLegitC) {
        btnLegitC.addEventListener("click", () => {
            applyPreset(4.50, 11000, [1.59, 0.57, 0.37, 0.85, -0.62, -0.17, 0.17, -0.15, 0.20, 0.20, -0.37, 0.06, 0.04, -0.08, -0.06, 0.15, 0.02, 0.19, -0.16, 0.08, -0.04, 0.02, 0.17, -0.06, 0.16, 0.02, 0.15, -0.02]);
        });
    }

    // ── Presets (NLP Tab) ──
    const nlpText = document.getElementById("nlp-text");
    document.querySelector(".preset-phish").addEventListener("click", () => {
        nlpText.value = "URGENT: Your HDFC Bank account is locked! Verify now at http://hdfc-secure-account.com or your account will be permanently disabled.";
    });
    document.querySelector(".preset-phish2").addEventListener("click", () => {
        nlpText.value = "Congratulations! You've won a $1,000 Walmart gift card. Click here to claim your prize before it expires: http://walmart-rewards-winner.com/claim";
    });
    document.querySelector(".preset-legit").addEventListener("click", () => {
        nlpText.value = "Your transaction of €150.00 at AMAZON.DE was successful on 14 Jul 2026. Ref: TXN-8472919.";
    });
    document.querySelector(".preset-legit2").addEventListener("click", () => {
        nlpText.value = "Hi John, just confirming our lunch meeting tomorrow at 12:30 PM. See you there!";
    });

    // ── API Submission Logic ──
    const resultsPane = document.getElementById("results-pane");
    const loadingOverlay = document.getElementById("loading-overlay");

    const showLoader = (text) => {
        document.getElementById("loading-text").textContent = text;
        loadingOverlay.classList.remove("hidden");
    };

    const hideLoader = () => {
        loadingOverlay.classList.add("hidden");
    };

    const displayResult = (data) => {
        resultsPane.classList.remove("hidden");
        
        const isFraud = (data.verdict === "FRAUD" || data.verdict === "FORGED" || data.verdict === "PHISHING" || data.verdict === "FRAUD/PHISHING");
        const vClass = isFraud ? "fraud" : "legit";
        const vIcon = isFraud ? "×" : "✓";
        const vText = data.verdict;
        
        let moduleCards = "";
        const icons = { ml: "📊", nlp: "💬", cv: "✍️" };
        const names = { ml: "ML · XGBOOST", nlp: "NLP · DISTILBERT", cv: "CV · SIAMESE" };

        let mlScore = 0;
        for (const [mod, res] of Object.entries(data.module_results)) {
            const modFraud = (res.verdict.includes("FRAUD") || res.verdict.includes("PHISH") || res.verdict.includes("FORGED"));
            const modClass = modFraud ? "fraud" : "legit";
            const scoreColor = modFraud ? "var(--fraud-text)" : "var(--legit-text)";
            
            if (mod === "ml") mlScore = res.score;
            
            moduleCards += `
                <div class="module-card-white">
                    <div class="mc-icon">${icons[mod] || "🔎"}</div>
                    <div class="mc-title">${names[mod] || mod.toUpperCase()}</div>
                    <div class="mc-score" style="color:${scoreColor}">${res.score.toFixed(3)}</div>
                    <div class="mc-pill ${modClass}">${res.verdict}</div>
                </div>
            `;
        }
        
        const fusionScorePct = (data.final_score * 100).toFixed(0);
        const mlScorePct = (mlScore * 100).toFixed(0);

        resultsPane.innerHTML = `
            <div class="verdict-banner ${vClass}">
                <div class="verdict-icon">
                    <div class="verdict-icon-circle">${vIcon}</div>
                </div>
                <div id="verdict-title">${vText} DETECTED</div>
                <div id="verdict-confidence">Confidence: <strong>${data.confidence}%</strong> &nbsp;·&nbsp; Fusion Score: <strong>${data.final_score.toFixed(4)}</strong></div>
            </div>

            <div class="scores-grid">
                <div class="score-card">
                    <div class="radial-progress" style="background: conic-gradient(var(--${vClass}-text) ${fusionScorePct}%, var(--border-card) 0%);">
                        <div class="radial-inner">${fusionScorePct}%</div>
                    </div>
                    <div class="score-title">FUSION SCORE</div>
                </div>
                <div class="score-card">
                    <div class="radial-progress" style="background: conic-gradient(var(--${mlScore > 0.5 ? 'fraud' : 'legit'}-text) ${mlScorePct}%, var(--border-card) 0%);">
                        <div class="radial-inner">${mlScorePct}%</div>
                    </div>
                    <div class="score-title">ML SCORE</div>
                </div>
            </div>

            <div class="score-bars-container">
                <div class="linear-score-row">
                    <div class="linear-score-header">
                        <span>Fusion Score</span>
                        <span class="val">${data.final_score.toFixed(4)}</span>
                    </div>
                    <div class="linear-bar-bg">
                        <div class="linear-bar-fill" style="width:${fusionScorePct}%; background:var(--${vClass}-text);"></div>
                    </div>
                </div>
                <div class="linear-score-row">
                    <div class="linear-score-header">
                        <span>ML Score</span>
                        <span class="val">${mlScore.toFixed(4)}</span>
                    </div>
                    <div class="linear-bar-bg">
                        <div class="linear-bar-fill" style="width:${mlScorePct}%; background:var(--${mlScore > 0.5 ? 'fraud' : 'legit'}-text);"></div>
                    </div>
                </div>
            </div>

            <div class="module-breakdown-section">
                <div class="breakdown-header">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
                    MODULE BREAKDOWN
                </div>
                <div class="breakdown-grid">
                    ${moduleCards}
                </div>
            </div>
        `;
    };

    // ML Submit
    document.getElementById("ml-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        showLoader("Analyzing Transaction...");
        
        // Construct 30 features array
        let features = new Array(30).fill(0.0);
        features[0] = parseFloat(document.getElementById("f-time").value);
        
        // Loop V1 to V28
        for(let i=1; i<=28; i++) {
            features[i] = parseFloat(document.getElementById(`f-v${i}`).value);
        }
        
        features[29] = parseFloat(document.getElementById("f-amount").value);

        const formData = new FormData();
        formData.append("transaction_features", JSON.stringify(features));

        try {
            const res = await fetch("/api/predict", { method: "POST", body: formData });
            const data = await res.json();
            displayResult(data);
        } catch (err) {
            console.error(err);
            alert("Error running prediction. Check console.");
        } finally {
            hideLoader();
        }
    });

    // NLP Submit
    document.getElementById("nlp-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const text = document.getElementById("nlp-text").value;
        if(!text.trim()) return;

        showLoader("Analyzing Text...");
        
        const formData = new FormData();
        formData.append("transaction_text", text);

        try {
            const res = await fetch("/api/predict", { method: "POST", body: formData });
            const data = await res.json();
            displayResult(data);
        } catch (err) {
            console.error(err);
            alert("Error running prediction.");
        } finally {
            hideLoader();
        }
    });

    // CV Submit
    document.getElementById("cv-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const refImg = document.getElementById("ref-img").files[0];
        const testImg = document.getElementById("test-img").files[0];
        
        if(!refImg || !testImg) return;

        showLoader("Verifying Signatures...");
        
        const formData = new FormData();
        formData.append("ref_image", refImg);
        formData.append("test_image", testImg);

        try {
            const res = await fetch("/api/predict", { method: "POST", body: formData });
            const data = await res.json();
            displayResult(data);
        } catch (err) {
            console.error(err);
            alert("Error running prediction.");
        } finally {
            hideLoader();
        }
    });
});
