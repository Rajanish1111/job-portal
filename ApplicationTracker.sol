// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

/**
 * @title ApplicationTracker
 * @dev A smart contract to create a verifiable and transparent record of job applications.
 */
contract ApplicationTracker {

    struct Application {
        uint id;
        address applicant;
        string jobTitle;
        string status; // e.g., "Applied", "Interviewing", "Offer", "Rejected"
        uint256 timestamp;
    }

    // A mapping from a user's address to an array of their application IDs
    mapping(address => uint[]) public userApplications;

    // Array to store all applications. The index is the application ID.
    Application[] public applications;

    // Event to be emitted when an application status is updated or created
    event ApplicationStatusUpdated(uint indexed applicationId, address indexed applicant, string status, uint256 timestamp);

    /**
     * @dev Creates a new application record on the blockchain.
     * @param _jobTitle The title of the job applied for.
     */
    function createApplication(string memory _jobTitle) public {
        uint applicationId = applications.length;
        
        applications.push(Application({
            id: applicationId,
            applicant: msg.sender,
            jobTitle: _jobTitle,
            status: "Applied", // Initial status is always "Applied"
            timestamp: block.timestamp
        }));

        userApplications[msg.sender].push(applicationId);

        emit ApplicationStatusUpdated(applicationId, msg.sender, "Applied", block.timestamp);
    }

    /**
     * @dev Allows updating the status of an existing application.
     * In a real scenario, this would have access control (e.g., only a company can update).
     * @param _applicationId The ID of the application to update.
     * @param _newStatus The new status of the application.
     */
    function updateApplicationStatus(uint _applicationId, string memory _newStatus) public {
        require(_applicationId < applications.length, "Application does not exist.");
        // Add access control here in a real application
        
        Application storage app = applications[_applicationId];
        app.status = _newStatus;
        app.timestamp = block.timestamp;

        emit ApplicationStatusUpdated(_applicationId, app.applicant, _newStatus, block.timestamp);
    }

    /**
     * @dev Retrieves all application records for the calling user.
     * @return A memory array of Application structs.
     */
    function getMyApplications() public view returns (Application[] memory) {
        uint[] memory applicationIds = userApplications[msg.sender];
        Application[] memory myApps = new Application[](applicationIds.length);

        for (uint i = 0; i < applicationIds.length; i++) {
            myApps[i] = applications[applicationIds[i]];
        }

        return myApps;
    }
}