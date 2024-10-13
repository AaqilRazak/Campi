import React from 'react';
import LoginForm from '../components/LoginForm';
import styles from '../styles/LoginPage.module.css';

const LoginPage = () => {
  return (
    <div className={styles.loginPage}>
      <h1>Login to Campi</h1>
      <LoginForm />
    </div>
  );
};

export default LoginPage;
