import time
import re

def invoke_llm_with_retry(chain, inputs, max_retries=5):
    """
    Invokes a LangChain chain with automatic retry logic if a 429 Rate Limit error occurs.
    Parses the suggested retry wait time from the exception message.
    """
    for attempt in range(max_retries):
        try:
            return chain.invoke(inputs)
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "rate_limit" in err_str:
                # Try to parse wait time from error message, e.g., "Please try again in 610ms" or "try again in 5.4s"
                wait_time = 3.0
                match = re.search(r"try again in (\d+\.?\d*)(m?s)", err_str)
                if match:
                    try:
                        val = float(match.group(1))
                        unit = match.group(2)
                        if unit == "ms":
                            wait_time = (val / 1000.0) + 0.5
                        else:
                            wait_time = val + 0.5
                    except ValueError:
                        pass
                # Add an incremental backoff based on attempt count
                wait_time += attempt * 1.5
                print(f"Rate limit (429) hit. Sleeping for {wait_time:.2f}s before retry (attempt {attempt + 1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                raise e
    raise Exception("Max retries exceeded for LLM call due to rate limits (429)")
