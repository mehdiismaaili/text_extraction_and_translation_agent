document.getElementById("action").addEventListener("change", function() {
  var translationOptions = document.getElementById("translationOptions");
  if (this.value === "translate") {
      translationOptions.style.display = "block";
  } else {
      translationOptions.style.display = "none";
  }
});

document.getElementById("processForm").addEventListener("submit", async function(e) {
  e.preventDefault();
  
  const imageFile = document.getElementById("image_file").files[0];
  const action = document.getElementById("action").value;
  const inLang = document.getElementById("in_lang").value;
  const destLang = document.getElementById("dest_lang") ? document.getElementById("dest_lang").value : "";

  // ✅ Client-Side Validation
  if (!imageFile) {
      alert("يرجى تحميل صورة قبل المتابعة.");
      return;
  }
  
  if (!action) {
      alert("يرجى تحديد ما إذا كنت تريد استخراج النص فقط أو الترجمة.");
      return;
  }

  if (!inLang) {
      alert("يرجى تحديد لغة النص في الصورة.");
      return;
  }

  if (action === "translate" && !destLang) {
      alert("يرجى تحديد لغة الترجمة.");
      return;
  }

  const formData = new FormData(e.target);

  try {
      const response = await fetch("/process", {
          method: "POST",
          body: formData
      });

      const data = await response.json();
      const outputDiv = document.getElementById("output");
      const finalText = document.getElementById("finalText");
      const readabilityDiv = document.getElementById("readability");
      const readabilityScore = document.getElementById("readabilityScore");
      const styleIssuesDiv = document.getElementById("styleIssues");
      const styleIssuesList = document.getElementById("styleIssuesList");

      if (data.error) {
          finalText.textContent = "خطأ: " + data.error;
          readabilityDiv.style.display = "none";
          styleIssuesDiv.style.display = "none";
      } else {
          if (typeof data.result === "string") {
              finalText.textContent = data.result;
              readabilityDiv.style.display = "none";
              styleIssuesDiv.style.display = "none";
          } else {
              finalText.textContent = data.result.translated_text;
              readabilityScore.textContent = `درجة السهولة: ${data.result.readability_score}`;

              readabilityDiv.style.display = data.result.readability_score ? "block" : "none";

              styleIssuesList.innerHTML = "";
              if (data.result.style_issues && data.result.style_issues.length > 0) {
                  data.result.style_issues.forEach(issue => {
                      let li = document.createElement("li");
                      li.textContent = issue.message;
                      styleIssuesList.appendChild(li);
                  });
                  styleIssuesDiv.style.display = "block";
              } else {
                  styleIssuesDiv.style.display = "none";
              }
          }
      }
      outputDiv.style.display = "block";
  } catch (error) {
      alert("حدث خطأ أثناء معالجة الطلب. الرجاء المحاولة مرة أخرى.");
      console.error("Error:", error);
  }
});

document.getElementById("copyBtn").addEventListener("click", function() {
  const textToCopy = document.getElementById("finalText").textContent;
  navigator.clipboard.writeText(textToCopy).then(function() {
      alert("تم نسخ النص!");
  }, function(err) {
      alert("حدث خطأ أثناء النسخ!");
  });
});
