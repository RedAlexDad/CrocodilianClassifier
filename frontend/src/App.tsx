import { Provider } from 'react-redux';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { store } from './app/store/store';
import { ClassifierWidget } from './widgets/Classifier/ClassifierWidget';
import { ModelManagementWidget } from './widgets/ModelManagement/ModelManagementWidget';
import { GalleryWidget } from './widgets/Gallery/GalleryWidget';
import './index.css';

const queryClient = new QueryClient();

function App() {
  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <div className="fixed-header">
            <div className="container">
              <nav className="navbar">
                <Link to="/" className="nav-link">Классификация</Link>
                <Link to="/gallery" className="nav-link">Галерея</Link>
                <Link to="/models" className="nav-link">Управление моделями</Link>
              </nav>
            </div>
          </div>

          <div className="container">
            <Routes>
              <Route path="/" element={<ClassifierWidget />} />
              <Route path="/gallery" element={<GalleryWidget />} />
              <Route path="/models" element={<ModelManagementWidget />} />
            </Routes>
          </div>

          <div className="fixed-footer">
            <div className="container">
              Домашнее задание №1 | РНС | МГТУ им. Баумана
            </div>
          </div>
        </BrowserRouter>
      </QueryClientProvider>
    </Provider>
  );
}

export default App;