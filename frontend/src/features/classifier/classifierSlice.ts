import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';

export interface PredictionResult {
  scorePrediction: string;
  image_url: string;
}

interface ClassifierState {
  selectedFile: File | null;
  imageUrl: string | null;
  prediction: PredictionResult | null;
  isLoading: boolean;
  error: string | null;
  availableModels: string[];
}

const initialState: ClassifierState = {
  selectedFile: null,
  imageUrl: null,
  prediction: null,
  isLoading: false,
  error: null,
  availableModels: [],
};

export const classifyImage = createAsyncThunk(
  'classifier/classify',
  async (formData: FormData) => {
    const response = await axios.post('/predictImage', formData);
    return response.data;
  }
);

const classifierSlice = createSlice({
  name: 'classifier',
  initialState,
  reducers: {
    setSelectedFile: (state, action: PayloadAction<{ file: File; url: string }>) => {
      state.selectedFile = action.payload.file;
      state.imageUrl = action.payload.url;
      state.prediction = null;
      state.error = null;
    },
    clearPrediction: (state) => {
      state.selectedFile = null;
      state.imageUrl = null;
      state.prediction = null;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(classifyImage.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(classifyImage.fulfilled, (state, action) => {
        state.isLoading = false;
        state.prediction = action.payload;
      })
      .addCase(classifyImage.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Ошибка классификации';
      });
  },
});

export const { setSelectedFile, clearPrediction } = classifierSlice.actions;
export default classifierSlice.reducer;