import { createRouter, createWebHistory } from 'vue-router';
import LandingPage from '../components/LandingPage.vue';
import PolicyBrowse from '../components/PolicyBrowse.vue';
import PolicyDetail from '../components/PolicyDetail.vue';
import PolicyRecommend from '../components/PolicyRecommend.vue';
import ProfilePage from '../components/ProfilePage.vue';

const routes = [
  { path: '/', name: 'home', component: LandingPage },
  { path: '/browse', name: 'browse', component: PolicyBrowse },
  { path: '/policy/:id', name: 'policy-detail', component: PolicyDetail },
  { path: '/recommend', name: 'recommend', component: PolicyRecommend },
  { path: '/profile', name: 'profile', component: ProfilePage },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

export default router;
