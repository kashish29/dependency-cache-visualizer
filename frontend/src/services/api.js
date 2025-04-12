// Base URL for the backend API
// During development with proxy, we can use relative paths starting with /api
// For standalone builds, this might need to be configurable.
const API_BASE_URL = '/api';

/**
 * Helper function for making API requests.
 * @param {string} endpoint - The API endpoint (e.g., '/tree').
 * @param {object} options - Fetch options (method, headers, body, etc.).
 * @returns {Promise<any>} - The JSON response data.
 * @throws {Error} - Throws an error if the request fails or response is not ok.
 */
const fetchApi = async (endpoint, options = {}) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const defaultHeaders = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    };

    const config = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
    };

    try {
        const response = await fetch(url, config);

        if (!response.ok) {
            let errorData;
            try {
                errorData = await response.json(); // Try to parse error details
            } catch (e) {
                errorData = { detail: `HTTP error! status: ${response.status}` };
            }
            console.error("API Error Response:", errorData);
            throw new Error(errorData.detail || `Request failed with status ${response.status}`);
        }

        // Handle cases where response might be empty (e.g., 204 No Content)
        if (response.status === 204) {
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error(`API request failed for endpoint ${endpoint}:`, error);
        // Re-throw the error so calling components can handle it
        throw error;
    }
};

// --- API Service Functions ---

export const getTree = () => {
    return fetchApi('/tree');
};

export const getStats = () => {
    return fetchApi('/stats');
};

export const resetStats = () => {
    return fetchApi('/reset-stats', { method: 'POST' });
};

export const getData = (path) => {
    if (!Array.isArray(path)) {
        throw new Error("Path must be an array of strings.");
    }
    return fetchApi('/get-data', {
        method: 'POST',
        body: JSON.stringify({ path }),
    });
};

export const addData = (path, data) => {
     if (!Array.isArray(path)) {
        throw new Error("Path must be an array of strings.");
    }
    return fetchApi('/add-data', {
        method: 'POST',
        body: JSON.stringify({ path, data }),
    });
};

export const invalidatePath = (path) => {
     if (!Array.isArray(path)) {
        throw new Error("Path must be an array of strings.");
    }
    return fetchApi('/invalidate', {
        method: 'POST',
        body: JSON.stringify({ path }),
    });
};

// Optional: Add function for data preview if implemented
// export const getDataPreview = (path) => {
//     if (!Array.isArray(path)) {
//         throw new Error("Path must be an array of strings.");
//     }
//     return fetchApi('/get-data-preview', {
//         method: 'POST',
//         body: JSON.stringify({ path }),
//     });
// };