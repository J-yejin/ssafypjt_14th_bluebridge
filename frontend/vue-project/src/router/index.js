import { createRouter, createWebHistory } from 'vue-router';
import LandingPage from '../views/LandingPage.vue';
import PolicyBrowse from '../views/PolicyBrowse.vue';
import PolicyDetail from '../views/PolicyDetail.vue';
import PolicyRecommend from '../views/PolicyRecommend.vue';
import ProfilePage from '../views/ProfilePage.vue';
import LoginView from '../views/LoginView.vue';
import SignupView from '../views/SignupView.vue';

const routes = [
  { path: '/', name: 'home', component: LandingPage },
  { path: '/browse', name: 'browse', component: PolicyBrowse },
  { path: '/policy/:id', name: 'policy-detail', component: PolicyDetail },
  { path: '/recommend', name: 'recommend', component: PolicyRecommend },
  { path: '/profile', name: 'profile', component: ProfilePage },
   { path: '/login', name: 'login', component: LoginView },
   { path: '/signup', name: 'signup', component: SignupView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

export default router;
