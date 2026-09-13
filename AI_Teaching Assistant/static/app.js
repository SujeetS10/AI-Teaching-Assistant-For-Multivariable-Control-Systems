// AI Teaching Assistant — frontend logic.
// Talks only to this app's own FastAPI backend (/api/ask). Never calls
// Groq directly, and never handles any API key.

const MAX_QUESTION_LENGTH = 2000;

const form = document.getElementById("ask-form");
const regInput = document.getElementById("reg-no");
const questionInput = document.getElementById("question");
const charCount = document.getElementById("char-count");
const regError = document.getElementById("reg-no-error");
const questionError = document.getElementById("question-error");
const requestError = document.getElementById("request-error");
const askBtn = document.getElementById("ask-btn");
const clearBtn = document.getElementById("clear-btn");
const loading = document.getElementById("loading");
const answerBody = document.getElementById("answer-body");

// Math is extracted from the raw text and rendered directly with KaTeX
// BEFORE Markdown ever sees it (see renderAnswer/extractMath below). This
// avoids two problems with running Markdown and math together: Markdown's
// GFM tables split on "|", which breaks LaTeX absolute-value/norm bars
// like $|x|_\infty$; and Markdown's backslash-escaping rules silently
// strip backslashes (\, and \! become , and !) inside anything it doesn't
// recognize as protected math. Pulling math out first sidesteps both.

// Live character count for the question textarea.
questionInput.addEventListener("input", () => {
  charCount.textContent = questionInput.value.length;
});

function showFieldError(el, message) {
  el.textContent = message;
  el.hidden = false;
}

function clearFieldErrors() {
  regError.hidden = true;
  questionError.hidden = true;
  requestError.hidden = true;
}

function validate(regNo, question) {
  let valid = true;

  if (!regNo) {
    showFieldError(regError, "Registration number is required.");
    valid = false;
  }

  if (!question) {
    showFieldError(questionError, "Please enter a question.");
    valid = false;
  } else if (question.length > MAX_QUESTION_LENGTH) {
    showFieldError(
      questionError,
      `Question is too long (max ${MAX_QUESTION_LENGTH} characters).`
    );
    valid = false;
  }

  return valid;
}

function setLoading(isLoading) {
  loading.hidden = !isLoading;
  askBtn.disabled = isLoading;
  askBtn.textContent = isLoading ? "Thinking…" : "Ask question";
}

// Pull every $$...$$ (display) and $...$ (inline) math expression out of
// the raw text, replacing each with a plain placeholder token that has no
// characters Markdown treats specially. Returns the placeholder text plus
// the list of extracted { display, latex } expressions, in order.
function extractMath(text) {
  const blocks = [];

  function stash(display, latex) {
    const token = `@@MATHBLOCK${blocks.length}@@`;
    blocks.push({ display, latex: latex.trim() });
    return token;
  }

  // Display math first ($$...$$), so a lone inner "$" can't be mistaken
  // for the start of a separate inline expression.
  let out = text.replace(/\$\$([\s\S]+?)\$\$/g, (_, expr) => stash(true, expr));

  // Inline math ($...$), single line only, not immediately adjacent to
  // another $ (so it doesn't pick up stray/unmatched $$ leftovers).
  out = out.replace(/\$([^\$\n]+?)\$/g, (_, expr) => stash(false, expr));

  return { text: out, blocks };
}

// Render each placeholder back into real KaTeX HTML inside the already
// Markdown-rendered HTML string.
function reinsertMath(html, blocks) {
  return html.replace(/@@MATHBLOCK(\d+)@@/g, (match, i) => {
    const block = blocks[Number(i)];
    if (!block) return match;
    try {
      return katex.renderToString(block.latex, {
        throwOnError: false,
        displayMode: block.display,
        // "html" only - skips KaTeX's hidden MathML accessibility copy,
        // which otherwise tends to get included when someone copies text
        // out of the page, making it look duplicated.
        output: "html",
      });
    } catch (err) {
      // Fall back to showing the raw LaTeX rather than losing the content.
      return block.display ? `$$${block.latex}$$` : `$${block.latex}$`;
    }
  });
}

function renderAnswer(text) {
  // The model sometimes writes LaTeX with \( \) and \[ \] delimiters
  // (common in GPT-style output) instead of $ $ and $$ $$. Normalize to
  // the $ / $$ form used below.
  const normalized = text
    .replace(/\\\(/g, "$")
    .replace(/\\\)/g, "$")
    .replace(/\\\[/g, "$$")
    .replace(/\\\]/g, "$$");

  if (window.marked && window.katex && window.DOMPurify) {
    const { text: protectedText, blocks } = extractMath(normalized);
    let html = marked.parse(protectedText);
    html = reinsertMath(html, blocks);
    answerBody.innerHTML = DOMPurify.sanitize(html, {
      // KaTeX's HTML-only output uses inline SVG for square-root symbols,
      // overlines, and stretchy delimiters, plus inline "style" attributes
      // for precise spacing - all of which DOMPurify's default config
      // would otherwise strip.
      ADD_TAGS: ["svg", "path", "line", "rect"],
      ADD_ATTR: ["style", "viewBox", "preserveAspectRatio", "d", "fill", "stroke", "width", "height", "xmlns"],
    });
  } else {
    // Fallback if the CDN scripts failed to load: at least show plain text.
    console.warn(
      "[app.js] marked/katex/DOMPurify not loaded - showing plain text. " +
      "Check your internet connection or whether a firewall/ad-blocker " +
      "is blocking cdn.jsdelivr.net."
    );
    answerBody.innerHTML = "";
    const p = document.createElement("p");
    p.textContent = text;
    answerBody.appendChild(p);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearFieldErrors();

  const regNo = regInput.value.trim();
  const question = questionInput.value.trim();

  if (!validate(regNo, question)) {
    return;
  }

  setLoading(true);

  try {
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        registration_no: regNo,
        question: question,
      }),
    });

    if (!response.ok) {
      let message = "Something went wrong. Please try again.";
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          message =
            typeof errorData.detail === "string"
              ? errorData.detail
              : "Please check your input and try again.";
        }
      } catch (_) {
        // Response body wasn't JSON — keep the default message.
      }
      showFieldError(requestError, message);
      return;
    }

    const data = await response.json();
    renderAnswer(data.answer);
  } catch (err) {
    showFieldError(
      requestError,
      "Could not reach the server. Check your connection and try again."
    );
  } finally {
    setLoading(false);
  }
});

clearBtn.addEventListener("click", () => {
  form.reset();
  charCount.textContent = "0";
  clearFieldErrors();
  answerBody.innerHTML =
    '<p class="answer__placeholder">Your answer will appear here once you ask a question.</p>';
});
