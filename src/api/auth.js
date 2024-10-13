export const login = async (username, password) => {
  // Replace this with actual API call
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (username === 'student' && password === 'password') {
        resolve({ role: 'student' });
      } else if (username === 'admin' && password === 'adminpass') {
        resolve({ role: 'admin' });
      } else {
        reject(new Error('Invalid username or password'));
      }
    }, 1000); // Simulate network delay
  });
};
