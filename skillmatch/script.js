let lastExtractedSkills = null;

function extractSkills() {
  const fileInput = document.getElementById('resumeFile');
  const output = document.getElementById('output');

  if (!fileInput.files.length) {
    output.innerHTML = '<p>Please upload a resume first.</p>';
    return;
  }

  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append('resume', file);

  output.innerHTML = '<p><i class="fas fa-spinner fa-spin"></i> Processing resume...</p>';

  fetch('/extract', {
    method: 'POST',
    body: formData,
  })
    .then(response => response.json())
    .then(data => {
      const skills = data.categorized_skills;
      if (skills && Object.keys(skills).length > 0) {
        lastExtractedSkills = skills;  // ✅ store globally for analyzeSkills()
        let html = `<h3>✅ Categorized Skills Extracted:</h3>`;
        for (let category in skills) {
          html += `<strong>${category}:</strong> <ul>`;
          skills[category].forEach(skill => {
            html += `<li>${skill}</li>`;
          });
          html += `</ul>`;
        }
        output.innerHTML = html;
      } else {
        output.innerHTML = '<p>No skills found in the resume.</p>';
      }
    })
    .catch(error => {
      output.innerHTML = `<p>Error: ${error.message}</p>`;
    });
}

function analyzeSkills() {
  const roleInput = document.getElementById('jobRole').value.trim();
  const output = document.getElementById('output');

  if (!lastExtractedSkills) {
    output.innerHTML = '<p>Please upload and extract resume skills first.</p>';
    return;
  }

  if (!roleInput) {
    output.innerHTML = '<p>Please enter a target job role.</p>';
    return;
  }

  output.innerHTML = '<p><i class="fas fa-spinner fa-spin"></i> Analyzing skill gap...</p>';

  fetch('/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      skills: lastExtractedSkills,
      role: roleInput
    })
  })
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        output.innerHTML = `<p>Error: ${data.error}</p>`;
        return;
      }

      let html = `<h3>🎯 Skill Gap Analysis for <i>${data.target_role}</i>:</h3>`;
      html += `<p><strong>✅ Matched Skills:</strong> (${data.matched_skills.length})</p><ul>${data.matched_skills.map(skill => `<li>${skill}</li>`).join('')}</ul>`;
      html += `<p><strong>⚠️ Missing Skills:</strong> (${data.missing_skills.length})</p><ul>${data.missing_skills.map(skill => `<li>${skill}</li>`).join('')}</ul>`;
      output.innerHTML = html;
    })
    .catch(error => {
      output.innerHTML = `<p>Error: ${error.message}</p>`;
    });
}
