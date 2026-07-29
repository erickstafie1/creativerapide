// Inchide meniul mobil dupa ce se apasa un link (util pentru ancore pe aceeasi pagina).
const navToggle = document.getElementById('nav-toggle');
if (navToggle) {
  document.querySelectorAll('.nav-links a').forEach(a => {
    a.addEventListener('click', () => { navToggle.checked = false; });
  });
}
