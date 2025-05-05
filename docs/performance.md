# Performance Report for TrendStory Microservice
**Target Machine:** Mac M4, 16GB RAM, 10-core GPU  
**Observed Story Generation Time:** ~35 seconds

---

## 1. System Architecture & Story Generation Flow
- The core story generation is handled by the `LLMEngine` class (`trendstory/llm_engine.py`), which uses the Dolphin LLM via the local Ollama API (`http://localhost:11434/api/generate`).
- The prompt is constructed with a detailed template and sent to the Ollama server, which runs the Dolphin model.
- The model is set to generate up to 500 tokens per story, with a high temperature and top-p for creativity.

---

## 2. Performance Bottlenecks Identified
### A. LLM Inference (Main Bottleneck)
- **Model:** Dolphin3 (as per config)
- **API:** Ollama (local, not remote, so no network latency)
- **Prompt:** Large, with detailed instructions and multiple constraints.
- **Token Limit:** 500 (`num_predict`)
- **Observed Generation Time:** 30–40 seconds per story is typical for large LLMs on consumer hardware, even with Apple Silicon.

### B. Hardware Utilization
- **CPU/GPU:** Ollama leverages Apple Silicon (M-series) but Dolphin3 is a large model, and Ollama's GPU acceleration is still maturing on Mac.
- **RAM:** 16GB is sufficient, but more RAM can help with larger models.
- **Concurrency:** The code is async, but only one story is generated at a time.

### C. Other Factors
- **Model Warmup:** The first request after starting Ollama may be slower due to model loading.
- **Prompt Size:** The prompt is verbose, which increases input token count and processing time.
- **No batching:** Each request is handled individually.

---

## 3. Performance Optimization Recommendations
### A. For Your Current Hardware
- **Keep Ollama and Dolphin3 up to date:** Newer versions may offer better Apple Silicon support and speed.
- **Reduce `num_predict`:** Lowering from 500 to 300–400 can cut generation time with minimal story quality loss.
- **Simplify Prompt:** Remove or condense some instructions if possible.
- **Monitor System Resources:** Use `Activity Monitor` or `htop` to ensure Ollama is using the GPU and not swapping RAM.
- **Warmup:** Run a dummy generation after starting Ollama to preload the model.

### B. Advanced
- **Try a smaller model:** If story quality is acceptable, use a lighter model (e.g., dolphin-mistral or llama2-7b) for faster results.
- **Increase RAM:** If you frequently multitask, 32GB+ will help with large models.
- **Experiment with Ollama settings:** Some users report better performance with different thread or memory settings.

---

## 4. Summary Table

| Step                | Typical Time | Notes                                      |
|---------------------|-------------|--------------------------------------------|
| Model Warmup        | 10–30s      | Only on first request after startup        |
| Story Generation    | 30–40s      | Main bottleneck, depends on model size     |
| Trends Fetching     | <1s         | Negligible                                 |
| Prompt Construction | <0.1s       | Negligible                                 |

---

## 5. Conclusion
- **Your observed 35s generation time is expected** for Dolphin3 on a Mac M4 with 16GB RAM.
- **Main bottleneck:** LLM inference speed in Ollama.
- **Best quick wins:** Reduce `num_predict`, try a smaller model, and keep Ollama updated.

---

_This report is tailored for your hardware and codebase. For any changes, update `docs/performance.md` as needed._
