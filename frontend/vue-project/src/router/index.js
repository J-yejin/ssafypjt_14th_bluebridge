import { createRouter, createWebHistory } from 'vue-router';
import LandingPage from '../views/LandingPage.vue';
import PolicyBrowse from '../views/PolicyBrowse.vue';
import PolicyDetail from '../views/PolicyDetail.vue';
import PolicyRecommend from '../views/PolicyRecommend.vue';
import ProfilePage from '../views/ProfilePage.vue';
import ProfileHub from '../views/ProfileHub.vue';
import ProfileWishlist from '../views/ProfileWishlist.vue';
import LoginView from '../views/LoginView.vue';
import SignupView from '../views/SignupView.vue';
import BoardListView from '../views/BoardListView.vue';
import BoardDetailView from '../views/BoardDetailView.vue';
import BoardCreateView from '../views/BoardCreateView.vue';
import OnboardingWizard from '../views/OnboardingWizard.vue';

const routes = [
  { path: '/', name: 'home', component: LandingPage },
  { path: '/browse', name: 'browse', component: PolicyBrowse },
  { path: '/policy/:id', name: 'policy-detail', component: PolicyDetail },
  { path: '/recommend', name: 'recommend', component: PolicyRecommend },
  { path: '/profile', name: 'profile', component: ProfileHub },
  { path: '/profile/edit', name: 'profile-edit', component: ProfilePage },
  { path: '/profile/wishlist', name: 'profile-wishlist', component: ProfileWishlist },
  { path: '/onboarding', name: 'onboarding', component: OnboardingWizard },
  { path: '/boards', name: 'boards', component: BoardListView },
  { path: '/boards/new', name: 'board-create', component: BoardCreateView },
  { path: '/boards/:id', name: 'board-detail', component: BoardDetailView },
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
