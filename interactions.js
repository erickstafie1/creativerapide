// Bara de progres de sus, urmareste scroll-ul paginii.
function initProgress() {
  const bar = document.querySelector('.progress-bar');
  if (!bar) return;
  window.addEventListener('scroll', () => {
    const max = document.body.scrollHeight - window.innerHeight;
    bar.style.transform = `scaleX(${max > 0 ? Math.min(window.scrollY / max, 1) : 0})`;
  }, { passive: true });
}

// Header capata umbra dupa primii 30px de scroll.
function initHeader() {
  const h = document.querySelector('header');
  if (!h) return;
  window.addEventListener('scroll', () => h.classList.toggle('scrolled', window.scrollY > 30), { passive: true });
}

// Elementele .rv si .reveal-group intra in vedere cu fade + slide, o singura data.
function initReveal() {
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    });
  }, { threshold: .12, rootMargin: '0px 0px -60px 0px' });
  document.querySelectorAll('.rv, .reveal-group').forEach(el => io.observe(el));
}

// Cifrele cu data-count numara de la 0 pana la valoarea reala cand intra in ecran.
function initCounters() {
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const el = e.target;
      const end = parseFloat(el.dataset.count);
      const suffix = el.dataset.suffix || '';
      let cur = 0;
      const step = Math.max(end / 40, 1);
      const iv = setInterval(() => {
        cur = Math.min(cur + step, end);
        el.textContent = Math.round(cur).toLocaleString('ro-RO') + suffix;
        if (cur >= end) clearInterval(iv);
      }, 20);
      io.unobserve(el);
    });
  }, { threshold: .5 });
  document.querySelectorAll('[data-count]').forEach(el => io.observe(el));
}

// Sagetile caruselului de recenzii deruleaza cate un slide.
function initCarousels() {
  document.querySelectorAll('.reviews-carousel').forEach(carousel => {
    const track = carousel.querySelector('.reviews-track');
    const prev = carousel.querySelector('.carousel-btn.prev');
    const next = carousel.querySelector('.carousel-btn.next');
    if (!track) return;
    const scrollByOne = dir => {
      const slide = track.querySelector('.review-slide');
      const amount = slide ? slide.getBoundingClientRect().width + 20 : track.clientWidth;
      track.scrollBy({ left: dir * amount, behavior: 'smooth' });
    };
    if (prev) prev.addEventListener('click', () => scrollByOne(-1));
    if (next) next.addEventListener('click', () => scrollByOne(1));
  });
}

initProgress();
initHeader();
initReveal();
initCounters();
initCarousels();
