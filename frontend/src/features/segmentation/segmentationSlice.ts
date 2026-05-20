import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

export interface Detection {
  class_id: number;
  class_name: string;
  confidence: number;
  bbox: [number, number, number, number];
  mask: {
    rle: number[];
    height: number;
    width: number;
  };
}

interface SegmenterState {
  imageUrl: string | null;
  detections: Detection[];
  isLoading: boolean;
  error: string | null;
}

const initialState: SegmenterState = {
  imageUrl: null,
  detections: [],
  isLoading: false,
  error: null,
};

const segmenterSlice = createSlice({
  name: 'segmenter',
  initialState,
  reducers: {
    setSegImage: (state, action: PayloadAction<{ url: string }>) => {
      state.imageUrl = action.payload.url;
      state.detections = [];
      state.error = null;
    },
    clearSegmentation: (state) => {
      state.imageUrl = null;
      state.detections = [];
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addMatcher(
        (action): action is { type: 'segmenter/segment/pending' } =>
          action.type === 'segmenter/segment/pending',
        (state) => {
          state.isLoading = true;
          state.error = null;
        },
      )
      .addMatcher(
        (action): action is { type: 'segmenter/segment/fulfilled'; payload: { image_url: string; detections: Detection[] } } =>
          action.type === 'segmenter/segment/fulfilled',
        (state, action) => {
          state.isLoading = false;
          state.imageUrl = action.payload.image_url;
          state.detections = action.payload.detections;
        },
      )
      .addMatcher(
        (action): action is { type: 'segmenter/segment/rejected'; payload: { message: string } } =>
          action.type === 'segmenter/segment/rejected',
        (state, action) => {
          state.isLoading = false;
          state.error = action.payload.message;
        },
      );
  },
});

export const { setSegImage, clearSegmentation } = segmenterSlice.actions;
export default segmenterSlice.reducer;
