/**
 * Sutanto Capital — Frontend Application
 * Reads initial data from window.__SC__ (injected by Jinja template).
 * For the complete standalone version, see sutanto_demo.html.
 */

(function() {
  'use strict';
  const SC = window.__SC__ || {};
  const deals = SC.deals || [];
  const myAssets = SC.myAssets || [];
  const peDeals = SC.peDeals || [];
  const apiStatus = SC.apiStatus || {};
  const mode = SC.mode || 'demo';

  // Tab switching
  window.switchTab = function(tab) {
    document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.getElementById('tab-' + tab).classList.add('active');
    const items = document.querySelectorAll('.nav-item');
    const map = { deals: 0, 'my-assets': 1, news: 2, 'pe-deals': 3 };
    if (map[tab] !== undefined) items[map[tab]].classList.add('active');
  };

  // Note: Full rendering logic is in the standalone HTML files.
  // This JS file is a skeleton for the Flask-served version.
  // In production, migrate the inline JS from sutanto_demo.html here.

  console.log('[Sutanto Capital] Mode:', mode, '| Deals:', deals.length, '| PE Deals:', peDeals.length);
})();
