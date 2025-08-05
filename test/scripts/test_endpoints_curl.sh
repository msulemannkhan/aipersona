#!/bin/bash

# Comprehensive endpoint testing script using curl
# This script tests all major endpoints with different user roles

BASE_URL="http://localhost:8000"
API_BASE="${BASE_URL}/api/v1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test credentials
declare -A TEST_USERS=(
    ["admin"]="admin@example.com:TestPass123!"
    ["counselor"]="counselor@example.com:TestPass123!"
    ["trainer"]="trainer@example.com:TestPass123!"
    ["user"]="user@example.com:TestPass123!"
)

# Store tokens
declare -A TOKENS

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    if [[ $status == "SUCCESS" ]]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [[ $status == "FAIL" ]]; then
        echo -e "${RED}❌ $message${NC}"
    elif [[ $status == "INFO" ]]; then
        echo -e "${BLUE}ℹ️  $message${NC}"
    elif [[ $status == "WARNING" ]]; then
        echo -e "${YELLOW}⚠️  $message${NC}"
    fi
}

# Function to login and get token
login_user() {
    local role=$1
    local credentials=${TEST_USERS[$role]}
    local email=$(echo $credentials | cut -d':' -f1)
    local password=$(echo $credentials | cut -d':' -f2)
    
    print_status "INFO" "Logging in $role user: $email"
    
    local response=$(curl -s -X POST "${API_BASE}/login/access-token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=${email}&password=${password}")
    
    local token=$(echo $response | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    
    if [[ -n $token ]]; then
        TOKENS[$role]=$token
        print_status "SUCCESS" "$role login successful"
        return 0
    else
        print_status "FAIL" "$role login failed: $response"
        return 1
    fi
}

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local role=$3
    local expected_status=$4
    local description=$5
    local data=$6
    
    local token=${TOKENS[$role]}
    if [[ -z $token ]]; then
        print_status "FAIL" "No token for $role"
        return 1
    fi
    
    local url="${API_BASE}${endpoint}"
    local curl_cmd="curl -s -X $method \"$url\" -H \"Authorization: Bearer $token\""
    
    if [[ -n $data ]]; then
        curl_cmd="$curl_cmd -H \"Content-Type: application/json\" -d '$data'"
    fi
    
    # Add -w option to get HTTP status code
    curl_cmd="$curl_cmd -w \"%{http_code}\""
    
    local response=$(eval $curl_cmd)
    local status_code=${response: -3}
    local body=${response%???}
    
    if [[ $status_code -eq $expected_status ]]; then
        print_status "SUCCESS" "$method $endpoint [$role] -> $status_code (expected $expected_status)"
        if [[ -n $description ]]; then
            echo "    $description"
        fi
        return 0
    else
        print_status "FAIL" "$method $endpoint [$role] -> $status_code (expected $expected_status)"
        if [[ -n $description ]]; then
            echo "    $description"
        fi
        echo "    Response: ${body:0:200}..."
        return 1
    fi
}

# Function to test authentication endpoints
test_authentication() {
    echo
    print_status "INFO" "🔐 Testing Authentication Endpoints"
    echo "----------------------------------------------------"
    
    # Login all users
    for role in "${!TEST_USERS[@]}"; do
        login_user $role
    done
    
    # Test current user endpoint
    for role in "${!TEST_USERS[@]}"; do
        test_endpoint "GET" "/users/me" $role 200 "Get current $role user info"
    done
}

# Function to test user management endpoints
test_user_management() {
    echo
    print_status "INFO" "👥 Testing User Management Endpoints"
    echo "----------------------------------------------------"
    
    # Admin should have access
    test_endpoint "GET" "/users/" "admin" 200 "Admin can list users"
    
    # Other roles should be denied
    for role in "counselor" "trainer" "user"; do
        test_endpoint "GET" "/users/" $role 403 "$role cannot list users"
    done
}

# Function to test AI souls endpoints
test_ai_souls() {
    echo
    print_status "INFO" "🤖 Testing AI Souls Endpoints"
    echo "----------------------------------------------------"
    
    # All authenticated users can view AI souls
    for role in "${!TEST_USERS[@]}"; do
        test_endpoint "GET" "/ai-souls/" $role 200 "$role can view AI souls"
    done
    
    # Only trainers and admins can create AI souls
    local ai_soul_data='{
        "name": "Test Soul",
        "description": "Test AI soul",
        "personality": "Helpful and friendly",
        "background": "Test background"
    }'
    
    for role in "trainer" "admin"; do
        test_endpoint "POST" "/ai-souls/" $role 200 "$role can create AI souls" "$ai_soul_data"
    done
    
    for role in "counselor" "user"; do
        test_endpoint "POST" "/ai-souls/" $role 403 "$role cannot create AI souls" "$ai_soul_data"
    done
}

# Function to test counselor endpoints
test_counselor_endpoints() {
    echo
    print_status "INFO" "👩‍⚕️ Testing Counselor Endpoints"
    echo "----------------------------------------------------"
    
    local counselor_endpoints=(
        "/counselor/queue"
        "/counselor/performance"
        "/counselor/risk-assessments"
    )
    
    for endpoint in "${counselor_endpoints[@]}"; do
        # Counselors and admins should have access
        for role in "counselor" "admin"; do
            test_endpoint "GET" "$endpoint" $role 200 "$role can access $endpoint"
        done
        
        # Other roles should be denied
        for role in "trainer" "user"; do
            test_endpoint "GET" "$endpoint" $role 403 "$role cannot access $endpoint"
        done
    done
}

# Function to test training endpoints
test_training_endpoints() {
    echo
    print_status "INFO" "🎓 Testing Training Endpoints"
    echo "----------------------------------------------------"
    
    # Get an AI soul ID first
    local token=${TOKENS["trainer"]}
    local souls_response=$(curl -s -X GET "${API_BASE}/ai-souls/" -H "Authorization: Bearer $token")
    local ai_soul_id=$(echo $souls_response | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
    
    if [[ -n $ai_soul_id ]]; then
        local training_message='{
            "content": "This is a test training message",
            "is_from_trainer": true
        }'
        
        # Only trainers and admins should access training endpoints
        for role in "trainer" "admin"; do
            test_endpoint "POST" "/training/$ai_soul_id/messages" $role 200 "$role can send training messages" "$training_message"
        done
        
        for role in "counselor" "user"; do
            test_endpoint "POST" "/training/$ai_soul_id/messages" $role 403 "$role cannot send training messages" "$training_message"
        done
    else
        print_status "WARNING" "No AI soul found for training tests"
    fi
}

# Function to test chat endpoints
test_chat_endpoints() {
    echo
    print_status "INFO" "💬 Testing Chat Endpoints"
    echo "----------------------------------------------------"
    
    # Get an AI soul ID first
    local token=${TOKENS["user"]}
    local souls_response=$(curl -s -X GET "${API_BASE}/ai-souls/" -H "Authorization: Bearer $token")
    local ai_soul_id=$(echo $souls_response | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
    
    if [[ -n $ai_soul_id ]]; then
        local chat_message='{
            "content": "Hello, this is a test message"
        }'
        
        # All authenticated users should be able to chat
        for role in "${!TEST_USERS[@]}"; do
            test_endpoint "POST" "/chat/$ai_soul_id/messages" $role 200 "$role can send chat messages" "$chat_message"
        done
    else
        print_status "WARNING" "No AI soul found for chat tests"
    fi
}

# Function to test role-based access summary
test_role_summary() {
    echo
    print_status "INFO" "🛡️ Role-Based Access Control Summary"
    echo "----------------------------------------------------"
    
    echo "Admin:"
    echo "  ✅ Can access: /users/, /ai-souls/, /counselor/queue, /training/*/messages, /chat/*/messages"
    echo "  ❌ Cannot access: (none - full access)"
    
    echo
    echo "Counselor:"
    echo "  ✅ Can access: /ai-souls/, /counselor/queue, /chat/*/messages"
    echo "  ❌ Cannot access: /users/, /training/*/messages"
    
    echo
    echo "Trainer:"
    echo "  ✅ Can access: /ai-souls/, /training/*/messages, /chat/*/messages"
    echo "  ❌ Cannot access: /users/, /counselor/queue"
    
    echo
    echo "User:"
    echo "  ✅ Can access: /ai-souls/, /chat/*/messages"
    echo "  ❌ Cannot access: /users/, /counselor/queue, /training/*/messages"
}

# Function to run all tests
run_all_tests() {
    echo "🚀 Starting Comprehensive Endpoint Testing"
    echo "============================================================"
    
    # Test authentication first
    test_authentication
    
    # Test role-specific endpoints
    test_user_management
    test_ai_souls
    test_counselor_endpoints
    test_training_endpoints
    test_chat_endpoints
    
    # Test role-based access summary
    test_role_summary
    
    echo
    echo "============================================================"
    print_status "SUCCESS" "Endpoint testing completed!"
    
    # Print login credentials for manual testing
    echo
    print_status "INFO" "📋 Test User Credentials:"
    echo "------------------------------"
    echo "Admin: admin@example.com / TestPass123!"
    echo "Counselor: counselor@example.com / TestPass123!"
    echo "Trainer: trainer@example.com / TestPass123!"
    echo "User: user@example.com / TestPass123!"
}

# Main execution
main() {
    # Check if curl is available
    if ! command -v curl &> /dev/null; then
        print_status "FAIL" "curl is not installed. Please install curl to run this script."
        exit 1
    fi
    
    # Check if server is running
    if ! curl -s "$BASE_URL/api/utils/health-check/" > /dev/null; then
        print_status "FAIL" "Server is not running at $BASE_URL"
        print_status "INFO" "Please make sure the backend server is running"
        exit 1
    fi
    
    print_status "SUCCESS" "Server is running at $BASE_URL"
    
    # Run all tests
    run_all_tests
}

# Run main function
main "$@" 