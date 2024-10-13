import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import InputField from './InputField';
import ErrorMessage from './ErrorMessage';
import { login } from '../api/auth';

const LoginForm = () => {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.username) newErrors.username = 'Username is required';
    if (!formData.password) newErrors.password = 'Password is required';
    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formErrors = validate();
    if (Object.keys(formErrors).length) {
      setErrors(formErrors);
      return;
    }
    setLoading(true);
    try {
      const user = await login(formData.username, formData.password);
      // Save user data to context or global state
      navigate(user.role === 'admin' ? '/admin' : '/chat');
    } catch (error) {
      setErrors({ general: error.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="login-form" onSubmit={handleSubmit}>
      <InputField
        type="text"
        name="username"
        value={formData.username}
        onChange={handleChange}
        placeholder="Username"
        error={errors.username}
      />
      <InputField
        type="password"
        name="password"
        value={formData.password}
        onChange={handleChange}
        placeholder="Password"
        error={errors.password}
      />
      {errors.general && <ErrorMessage message={errors.general} />}
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
};

export default LoginForm;
